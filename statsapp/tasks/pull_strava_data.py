import argparse
import datetime
import logging

import statsapp
from statsapp.models.oauth import fetch_token
from statsapp.models.strava import StravaActivity
from statsapp.models.user import User

# re-pull a little before the latest stored activity, to catch late uploads and edits
OVERLAP = datetime.timedelta(days=7)


class PullStravaData(object):

    def __init__(self, argv=None):
        self.setup_parser(argv)
        self.process_args()

    def setup_parser(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("--user-id", type=int, help="user_id to update for. If omitted, will update values for all users")
        parser.add_argument("--full", action="store_true", help="Pull every activity, not just ones since the most recent stored activity")

        self.args = parser.parse_args(argv)

    def process_args(self):
        self.user_id = self.args.user_id
        self.full = self.args.full

    def get_data_and_upsert(self, user):
        # statsapp.apis.strava reads app config at import time, so it can only be
        # imported once the app context exists
        from statsapp.apis.strava import StravaAPI

        after = None
        if not self.full:
            most_recent_start = StravaActivity.get_most_recent_start(user)
            if most_recent_start:
                after = most_recent_start - OVERLAP

        print(f"Getting strava activities for {user} after {after or 'the beginning'}")
        activities = StravaAPI.get_activities(user, after=after)
        print(f"Got {len(activities)} activities")

        for activity in activities:
            StravaActivity.upsert(
                user,
                activity['strava_id'],
                activity['sport_type'],
                activity['start_date_local'],
                activity['distance_metres']
            )

    def run(self):
        if not self.user_id:
            users = User.query.all()
        else:
            users = [User.query.get(self.user_id)]

        for user in users:
            # without a token of their own, authlib falls back to the default user's token
            if not fetch_token('strava', user):
                print(f"{user} has no strava token, skipping")
                continue
            try:
                self.get_data_and_upsert(user)
            except Exception as e:
                print(f"failed to get strava data for {user}")
                logging.exception(e)


if __name__ == '__main__':
    app = statsapp.create_app()
    with app.app_context():
        PullStravaData().run()
