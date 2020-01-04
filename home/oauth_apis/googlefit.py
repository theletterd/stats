import datetime
from datetime import timedelta
import time

from flask import current_app
from models import fetch_token

from . import oauth
oauth.register(
    name='googlefit',
    api_base_url='https://www.googleapis.com/fitness/v1/users/',
    # used to get a user's permissions
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params={
        'scope': 'https://www.googleapis.com/auth/fitness.activity.read https://www.googleapis.com/auth/fitness.body.read https://www.googleapis.com/auth/fitness.location.read',
        'access_type': 'offline'
    },
    # used for getting the token
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params={
        'client_id': current_app.config['GOOGLEFIT_CLIENT_ID'],
        'client_secret': current_app.config['GOOGLEFIT_CLIENT_SECRET'],
    }
)


class GoogleFitAPI(object):

    def get_stats_for_date(date, user):
        assert type(date) is datetime.date

        token = fetch_token('googlefit', user)

        start_date = datetime.datetime(date.year, date.month, date.day)
        end_date = start_date + timedelta(days=1)

        start_time = int(start_date.timestamp())
        end_time = int(end_date.timestamp())


        now = int(time.time())
        if end_time > now:
            end_time = now

        params = {
            "aggregateBy": [
                {
                    "dataTypeName": "com.google.step_count.delta",
                    "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
                },
                {
                    "dataTypeName": "com.google.weight.summary",
                    "dataSourceId": "derived:com.google.weight:com.google.android.gms:merge_weight"
                },
                {
                    "dataTypeName": "com.google.distance.delta",
                    "dataSourceId": "derived:com.google.distance.delta:com.google.android.gms:merge_distance_delta"
                }
            ],
            "bucketByTime": { "durationMillis": 86400000 },
            "startTimeMillis": start_time * 1000,
            "endTimeMillis": end_time * 1000
        }
        resp = oauth.googlefit.post('me/dataset:aggregate', json=params, token=token)
        json_response = resp.json()

        steps = 0
        distance_metres = 0
        weight_kg = None

        for bucket in json_response['bucket']:
            steps_datapoints = bucket['dataset'][0]['point']
            if steps_datapoints:
                steps += steps_datapoints[0]['value'][0]['intVal']

            distance_datapoints = bucket['dataset'][2]['point']
            if distance_datapoints:
                distance_metres += distance_datapoints[0]['value'][0]['fpVal']

        weight_datapoints = json_response['bucket'][0]['dataset'][1]['point']
        if weight_datapoints:
            weight_kg = weight_datapoints[0]['value'][0]['fpVal']

        return steps, distance_metres, weight_kg
