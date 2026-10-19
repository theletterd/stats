import datetime

from statsapp.models.strava import StravaActivity
from statsapp.models.user import User
from statsapp.models.withings import WithingsData


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
    assert b'y: 8000.0' in resp.data
