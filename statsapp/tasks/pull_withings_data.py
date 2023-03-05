import argparse
import datetime
import logging

import statsapp
from statsapp import db
from statsapp.apis.withings import WithingsAPI
from statsapp.models.user import User
from statsapp.models.withings import WithingsData
from statsapp.tools import util

date_parser = lambda s: datetime.date.fromisoformat(s)

class PullWithingsData(object):

    def __init__(self):
        self.setup_parser()
        self.process_args()

    def setup_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--user-id", type=int, help="user_id to update for. If omitted, will update values for all users")
        parser.add_argument("--start-date", type=date_parser, help="YYYY-MM-DD, date to start pulling data for. If omitted, defaults to yesterday")
        parser.add_argument("--end-date", type=date_parser, help="YYYY-MM-DD, date to pull data until (inclusive). If omitted, defaults to today")

        self.args = parser.parse_args()

    def process_args(self):
        self.end_date = self.args.end_date or util.today_pacific()
        self.start_date = self.args.start_date or (self.end_date - datetime.timedelta(days=1))
        self.user_id = self.args.user_id

    def get_data_and_upsert(self, date, user):
        print(f"Getting withings data for {user} on {date}")
        weight_kg = WithingsAPI.get_weight_data(date, user)
        print(f"{date}: weight - {weight_kg}")
        if weight_kg:
            WithingsData.upsert(
                user,
                date,
                weight_kg
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
                    self.get_data_and_upsert(date, user)
                except Exception as e:
                    print(f"failed to get data for {user} on {date}")
                    logging.exception(e)


if __name__ == '__main__':
    app = statsapp.create_app()
    with app.app_context():
        PullWithingsData().run()
