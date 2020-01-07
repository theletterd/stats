import argparse
import datetime
import logging

from statsapp import create_app
from statsapp.models.user import User
from statsapp.models.googlefit import GoogleFitData
from statsapp.tools import util

date_parser = lambda s: datetime.date.fromisoformat(s)

parser = argparse.ArgumentParser()
parser.add_argument("--user-id", type=int, help="user_id to update for. If omitted, will update values for all users")
parser.add_argument("--start-date", type=date_parser, help="YYYY-MM-DD, date to start pulling data for. If omitted, defaults to yesterday")
parser.add_argument("--end-date", type=date_parser, help="YYYY-MM-DD, date to pull data until (inclusive). If omitted, defaults to today")

args = parser.parse_args()

end_date = args.end_date or util.today_pacific()
start_date = args.start_date or (end_date - datetime.timedelta(days=1))
dates = util.get_dates_between(start_date, end_date)
user_id = args.user_id


app = create_app()
logging.info(f'start_date: {start_date}')
logging.info(f'end_date: {end_date}')
logging.info(f'user_id: {user_id}')


with app.app_context():

    # because oauth stuff needs to be initialised/imported inside an app context
    from statsapp.oauth_apis.googlefit import GoogleFitAPI

    if not user_id:
        users = User.query.all()
    else:
        users = [User.get_default_user()]

    for user in users:
        for date in dates:
            try:
                logging.info(f"Getting data for {user} on {date}")
                step_count, distance_metres, weight_kg = GoogleFitAPI.get_stats_for_date(date, user)
                GoogleFitData.upsert(
                    user,
                    date,
                    step_count,
                    distance_metres,
                    weight_kg
                )
            except Exception as e:
                logging.info(f"failed to get data for {user} on {date}")
                logging.exception(e)

