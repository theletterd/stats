import datetime
import time

from flask import current_app

from statsapp.models.oauth import fetch_token
from statsapp.tools.util import pdt

from . import oauth


oauth.register(
    name='withings',
    api_base_url='https://wbsapi.withings.net/',
    authorize_url='https://account.withings.com/oauth2_user/authorize2',
    authorize_params={'scope':'user.metrics'},
    access_token_url='https://account.withings.com/oauth2/token',
    access_token_params={
        "client_id": current_app.config["WITHINGS_CLIENT_ID"],
        "client_secret": current_app.config["WITHINGS_CLIENT_SECRET"]
    }
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
