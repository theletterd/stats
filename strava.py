import asyncio
from aiohttp_requests import requests

import datetime
import json

from secret import STRAVA_CODE
from secret import STRAVA_CLIENT_ID
from secret import STRAVA_CLIENT_SECRET


def convert_metres_to_miles_safe(metres):
    if not metres:
        return 0
    return metres / 1609.0


async def get_token():
    payload = {
        "code": STRAVA_CODE,
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "grant_type": "authorization_code"
    }
    print("getting token")
    resp = await requests.post("https://www.strava.com/oauth/token", data=payload)
    print("waiting for token")
    json = await resp.json()
    print("got token")

    return json['access_token']


async def get_stats():
    token = await get_token()

    headers = {"Authorization": f"Bearer {token}"}
    params = {"per_page": 200} # optimistically assuming I won't run more than 100 times a year on average. seems reasonable.
    print("getting data")
    resp = await requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers, params=params)
    print("waiting for data")
    json_response = await resp.json()
    print("got data")

    stats = {}

    for activity in json_response:
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

    distance_current_year = convert_metres_to_miles_safe(stats.get(current_year ,{}).get('distance_run_metres', 0))
    distance_last_year = convert_metres_to_miles_safe(stats.get(prev_year, {}).get('distance_run_metres', 0))

    constructed_stats = {
        'distance_run_current_year_miles': {
            'stat_id': 'distance_run_current_year_miles',
            'description': 'Distance this year (miles)',
            'value': f"{distance_current_year:.2f}"
        },
        'distance_run_prev_year_miles': {
            'stat_id': 'distance_run_prev_year_miles',
            'description': 'Distance last year (miles)',
            'value': f"{distance_last_year:.2f}"
        },
        'run_count_current_year': {
            'stat_id': 'run_count_current_year',
            'description': 'Runs this year',
            'value': stats.get(current_year, {}).get('run_count', 0)
        },
        'run_count_prev_year': {
            'stat_id': 'run_count_prev_year',
            'description': 'Runs last year',
            'value': stats.get(prev_year, {}).get('run_count', 0)
        },
    }

    return constructed_stats
