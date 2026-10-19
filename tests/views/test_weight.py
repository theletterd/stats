import datetime
import json
import re

from statsapp.models.strava import StravaActivity
from statsapp.models.user import User
from statsapp.models.withings import WithingsData


def _chart_data(page):
    match = re.search(r'<script id="chart-data" type="application/json">(.*?)</script>', page, re.S)
    return json.loads(match.group(1))


def test_weight_page_with_no_data(client):
    resp = client.get('/weight')
    assert resp.status_code == 200


def test_weight_page_with_data(client):
    user = User.get_default_user()
    WithingsData.upsert(user, datetime.date(2020, 1, 1), 80)
    StravaActivity.upsert(user, 1, 'Run', datetime.datetime(2020, 1, 2, 8), 5000)
    StravaActivity.upsert(user, 2, 'Run', datetime.datetime(2020, 1, 2, 18), 3000)

    resp = client.get('/weight')

    assert resp.status_code == 200
    chart_data = _chart_data(resp.data.decode())
    # two runs on the same day are summed into one bar
    assert chart_data['runs'] == [{'x': '2020-01-02', 'y': 8000.0}]
    assert len(chart_data['weight']) == 1
