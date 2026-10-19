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

    PAGE_SIZE = 200

    def get_activities(user, after=None):
        """
        Returns every activity for the user as a list of dicts
        with strava_id, sport_type, start_date_local and distance_metres.
        If `after` (a datetime) is given, only activities starting after it are returned.
        """
        token = fetch_token('strava', user)

        params = {"per_page": StravaAPI.PAGE_SIZE}
        if after:
            params["after"] = int(after.replace(tzinfo=datetime.timezone.utc).timestamp())

        activities = []
        page = 1
        while True:
            resp = oauth.strava.get('athlete/activities', params={**params, "page": page}, token=token)
            resp.raise_for_status()
            page_activities = resp.json()

            for activity in page_activities:
                activities.append(dict(
                    strava_id=activity['id'],
                    sport_type=activity['sport_type'],
                    start_date_local=datetime.datetime.strptime(activity['start_date_local'], '%Y-%m-%dT%H:%M:%SZ'),
                    distance_metres=activity['distance'],
                ))

            if len(page_activities) < StravaAPI.PAGE_SIZE:
                break
            page += 1

        return activities
