import argparse
import datetime
import logging

import statsapp
from statsapp import db
from statsapp import db_util
from statsapp.models.user import User
from statsapp.apis.googlefit import GoogleFitAPI
from statsapp.models.googlefit import GoogleFitData
from statsapp.models.googlefit import GoogleFitYoga
from statsapp.tools import util

date_parser = lambda s: datetime.date.fromisoformat(s)

class PullRecentGoogleFitData(object):

    def __init__(self, argv=None):
        self.setup_parser(argv)
        self.process_args()

    def setup_parser(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("--user-id", type=int, help="user_id to update for. If omitted, will update values for all users")
        parser.add_argument("--start-date", type=date_parser, help="YYYY-MM-DD, date to start pulling data for. If omitted, defaults to yesterday")
        parser.add_argument("--end-date", type=date_parser, help="YYYY-MM-DD, date to pull data until (inclusive). If omitted, defaults to today")

        self.args = parser.parse_args(argv)

    def process_args(self):
        self.end_date = self.args.end_date or util.today_pacific()
        self.start_date = self.args.start_date or (self.end_date - datetime.timedelta(days=7))
        self.user_id = self.args.user_id

    def get_step_data_and_upsert(self, date, user):
        print(f"Getting data for {user} on {date}")
        step_count, distance_metres = GoogleFitAPI.get_stats_for_date(date, user)
        print(f"{date}: steps - {step_count}, distance - {distance_metres}")
        GoogleFitData.upsert(
            user,
            date,
            step_count,
            distance_metres
        )

    def get_30_day_yoga_sessions(self, end_date, user):
        print(f"Getting yoga data for {user} 30 days previous to {end_date}")
        yoga_sessions = GoogleFitAPI.get_yoga_sessions(end_date, 30, user)
        for yoga_session in yoga_sessions:
            session_date = yoga_session['date']
            session_start_time = yoga_session['start_time']
            session_duration = yoga_session['duration_seconds']
            print(f"{session_date}: duration - {session_duration} seconds")
            GoogleFitYoga.upsert(
                user,
                session_date,
                session_start_time,
                session_duration
            )


    def run(self):
        dates = util.get_dates_between(self.start_date, self.end_date)

        if not self.user_id:
            users = User.query.all()
        else:
            users = [User.get_default_user()]

        for user in users:
            for date in dates:
                try:
                    self.get_step_data_and_upsert(date, user)
                except Exception as e:
                    print(f"failed to get data for {user} on {date}")
                    logging.exception(e)

            try:
                self.get_30_day_yoga_sessions(self.end_date, user)
            except Exception as e:
                print(f"failed to get yoga data for {user} ending on {self.end_date}")
                logging.exception(e)



if __name__ == '__main__':
    app = statsapp.create_app()
    with app.app_context():
        PullRecentGoogleFitData().run()
