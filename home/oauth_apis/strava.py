import datetime
from flask import current_app

from models import Stat

from . import oauth


def _strava_compliance_fix(session):
    """ Strava requires client_id and client_secret when refreshing the token"""
    def _add_client_secrets_to_refresh(url, headers, data):
        client_id = session.client_id
        client_secret = session.client_secret
        # TODO do this less jankily
        data = f"{data}&client_id={client_id}&client_secret={client_secret}"
        return url, headers, data

    session.register_compliance_hook(
        'refresh_token_request', _add_client_secrets_to_refresh
    )

oauth.register(
    name='strava',
    api_base_url='https://www.strava.com/api/v3/',
    authorize_url='https://www.strava.com/oauth/authorize',
    authorize_params={'scope': 'activity:read_all'},
    access_token_url='https://www.strava.com/oauth/token',
    access_token_params={
        "client_id": current_app.config['STRAVA_CLIENT_ID'],
        "client_secret": current_app.config['STRAVA_CLIENT_SECRET'],
    },
    compliance_fix=_strava_compliance_fix
)

#print(_client)

class StravaAPI(object):

    def _convert_metres_to_miles_safe(metres):
        if not metres:
            return 0
        return metres / 1609.0

    @classmethod
    def get_stats(klass):
        params = {"per_page": 200} # optimistically assuming I won't run more than 100 times a year on average. seems reasonable.
        resp = oauth.strava.get('athlete/activities', params=params)
        stats = {}

        for activity in resp.json():
            year = datetime.datetime.strptime(activity['start_date_local'],'%Y-%m-%dT%H:%M:%SZ').year
            distance_metres = activity['distance']

            if year not in stats:
                stats[year] = {
                    'run_count': 0,
                    'distance_run_metres': 0
                }

            stats[year]['run_count'] += 1
            stats[year]['distance_run_metres'] += distance_metres

        # construct stats
        current_year = datetime.date.today().year
        prev_year = current_year - 1

        distance_current_year = klass._convert_metres_to_miles_safe(stats.get(current_year ,{}).get('distance_run_metres', 0))
        distance_last_year = klass._convert_metres_to_miles_safe(stats.get(prev_year, {}).get('distance_run_metres', 0))

        constructed_stats = [
            Stat(
                stat_id='distance_run_current_year_miles',
                description='Distance this year (miles)',
                value=f"{distance_current_year:.2f}"
            ),
            Stat(
                stat_id='distance_run_prev_year_miles',
                description='Distance last year (miles)',
                value=f"{distance_last_year:.2f}"
            ),
            Stat(
                stat_id='run_count_current_year',
                description='Runs this year',
                value=stats.get(current_year, {}).get('run_count', 0)
            ),
            Stat(
                stat_id='run_count_prev_year',
                description='Runs last year',
                value=stats.get(prev_year, {}).get('run_count', 0)
            )
        ]

        return constructed_stats
