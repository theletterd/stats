import datetime
import time

from flask import current_app

from statsapp import config
from statsapp.models.oauth import fetch_token
from statsapp.tools.util import pdt

from . import oauth


def _withings_compliance_fix(session):
    """ Withings requires client_id and client_secret when refreshing the token"""
    def _add_client_secrets_to_refresh(url, headers, data):
        client_id = session.client_id
        client_secret = session.client_secret
        # TODO do this less jankily
        data = f"{data}&action=requesttoken&client_id={client_id}&client_secret={client_secret}"
        return url, headers, data

    def _fix_token_response(resp):
        # withings sticks all the token stuff in a `body` dict, so gonna just pull that up
        token_data = resp.json()['body']
        resp.json = lambda: token_data
        return resp

    session.register_compliance_hook(
        'refresh_token_request', _add_client_secrets_to_refresh
    )
    session.register_compliance_hook(
        'access_token_response', _fix_token_response
    )
    session.register_compliance_hook(
        'refresh_token_response', _fix_token_response
    )

oauth.register(
    name='withings',
    api_base_url='https://wbsapi.withings.net/',
    authorize_url='https://account.withings.com/oauth2_user/authorize2',
    authorize_params={'scope':'user.metrics'},
    access_token_url='https://wbsapi.withings.net/v2/oauth2',
    access_token_params={
        "client_id": config.WITHINGS_CLIENT_ID,
        "client_secret": config.WITHINGS_CLIENT_SECRET,
        "action": "requesttoken"
    },
    compliance_fix=_withings_compliance_fix
)


class WithingsAPI(object):

    def get_weight_data(date, user):
        token = fetch_token('withings', user)

        # this is a direct copy/paste from the googlefit api.
        # seems dumb.
        start_date = pdt.localize(datetime.datetime(date.year, date.month, date.day))
        end_date = start_date + datetime.timedelta(days=1)

        start_time = int(start_date.timestamp())
        end_time = int(end_date.timestamp())

        now = int(time.time())
        if end_time > now:
            end_time = now

        # see https://developer.withings.com/oauth2/#tag/measure
        params = {
            'action': 'getmeas',
            'meastype': 1, # weight
            'category': 1, # real measurements
            'startdate': start_time, # epochtime
            'enddate': end_time, # epochtime,
            'offset': 0 # only care about first reading
        }
        resp = oauth.withings.get('measure', token=token, params=params)
        json_response = resp.json()

        weight_kg = None

        measure_groups = json_response['body']['measuregrps']
        if measure_groups:
            measure = measure_groups[0]['measures'][0]
            weight_kg = measure['value'] * (10 ** measure['unit'])

        return weight_kg
