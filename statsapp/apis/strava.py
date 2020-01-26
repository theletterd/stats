import datetime

from flask import current_app

from statsapp.models.oauth import fetch_token
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


class StravaAPI(object):

    def get_run_data(user):
        token = fetch_token('strava', user)

        # optimistically assuming I won't run more than 100 times a year on average. seems reasonable.
        params = {"per_page": 200}
        resp = oauth.strava.get('athlete/activities', params=params, token=token)
        runs = []

        for activity in resp.json():
            date = datetime.datetime.strptime(activity['start_date_local'], '%Y-%m-%dT%H:%M:%SZ')
            distance_metres = activity['distance']
            runs.append((date, distance_metres))
        return runs

