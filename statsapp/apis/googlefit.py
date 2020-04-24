import datetime
import time

from flask import current_app

from statsapp.models.oauth import fetch_token
from statsapp.tools.util import pdt

from . import oauth
oauth.register(
    name='googlefit',
    api_base_url='https://www.googleapis.com/fitness/v1/users/',
    # used to get a user's permissions
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params={
        'scope': 'https://www.googleapis.com/auth/fitness.activity.read https://www.googleapis.com/auth/fitness.body.read https://www.googleapis.com/auth/fitness.location.read',
        'access_type': 'offline',
        'prompt': 'consent'
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

        start_date = pdt.localize(datetime.datetime(date.year, date.month, date.day))
        end_date = start_date + datetime.timedelta(days=1)

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
                    "dataTypeName": "com.google.distance.delta",
                    "dataSourceId": "derived:com.google.distance.delta:com.google.android.gms:merge_distance_delta"
                }
            ],
            "bucketByTime": {"durationMillis": 86400000},
            "startTimeMillis": start_time * 1000,
            "endTimeMillis": end_time * 1000
        }
        resp = oauth.googlefit.post('me/dataset:aggregate', json=params, token=token)
        json_response = resp.json()

        steps = 0
        distance_metres = 0
        for bucket in json_response['bucket']:
            steps_datapoints = bucket['dataset'][0]['point']
            if steps_datapoints:
                steps += steps_datapoints[0]['value'][0]['intVal']

            distance_datapoints = bucket['dataset'][1]['point']
            if distance_datapoints:
                distance_metres += distance_datapoints[0]['value'][0]['fpVal']

        return steps, distance_metres


    def get_yoga_sessions(end_date, num_days, user):
        assert type(end_date) is datetime.date

        token = fetch_token('googlefit', user)

        end_date = end_date + datetime.timedelta(days=1) # include anything that happened on that day.
        end_date = pdt.localize(datetime.datetime(end_date.year, end_date.month, end_date.day))
        start_date = end_date - datetime.timedelta(days=num_days)

        # really annoying, this has to be in rfc3339 (which is pretty comparable to iso8601)
        start_time = start_date.timestamp()
        end_time = end_date.timestamp()

        now = int(time.time())
        if end_time > now:
            end_time = now

        # oh yeah this is some bullshit.
        end_isoformat = datetime.datetime.fromtimestamp(end_time).isoformat() + "Z"
        start_isoformat = datetime.datetime.fromtimestamp(start_time).isoformat() + "Z"

        params = {
            "activityType": 100, # Yoga, from https://developers.google.com/fit/rest/v1/reference/activity-types
            "startTime": start_isoformat,
            "endTime": end_isoformat
        }
        resp = oauth.googlefit.get('me/sessions', params=params, token=token)
        json_response = resp.json()
        sessions = []
        for session in json_response["session"]:
            session_start_time = int(int(session["startTimeMillis"]) / 1000)
            session_end_time = int(int(session["endTimeMillis"]) / 1000)
            duration_seconds = (session_end_time - session_start_time)
            date = pdt.localize(datetime.datetime.fromtimestamp(session_start_time)).date()
            session_data = dict(
                start_time=session_start_time,
                duration_seconds=duration_seconds,
                date=date
            )
            sessions.append(session_data)

        return sessions
