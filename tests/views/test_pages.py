import datetime

import pytest

from statsapp.models.stat import Stat
from statsapp.models.user import User

# the collectors pull in API modules that read app config at import time, so
# they're imported inside the tests once the app fixture has set up a context


def _log_in(client):
    user = User.get_default_user()
    with client.session_transaction() as session:
        session['_user_id'] = str(user.id)


def test_dashboard_shell_renders(client):
    resp = client.get('/')

    assert resp.status_code == 200
    assert b'dashboard.js' in resp.data
    assert b'babel' not in resp.data.lower()


def test_login_page_renders(client):
    resp = client.get('/login')

    assert resp.status_code == 200
    assert b'name="csrf_token"' in resp.data


def test_apps_page_lists_missing_dates_in_order(client):
    _log_in(client)

    resp = client.get('/authorized_apps')

    assert resp.status_code == 200
    assert b'Connect Strava' in resp.data
    # each backfill chunk is labelled with its first and last date, so dates must be sorted
    page = resp.data.decode()
    first_date = page.index('name="date" value="')
    dates = [
        datetime.date.fromisoformat(chunk.split('"')[0])
        for chunk in page[first_date:].split('name="date" value="')[1:]
    ]
    assert dates == sorted(dates)


@pytest.fixture
def stub_collectors(mocker): # noqa
    from statsapp.collectors.goals import GoalStats
    from statsapp.collectors.goodreads import GoodreadsStats
    from statsapp.collectors.googlefit import GoogleFitStats
    from statsapp.collectors.googlefit import GoogleFitYogaStats
    from statsapp.collectors.gsheet import GoogleSheetsStats
    from statsapp.collectors.strava import StravaStats
    from statsapp.collectors.withings import WithingsStats

    stat = Stat(stat_id='age', description='Age', value='43', notes='')
    for collector in (GoogleFitStats, GoogleFitYogaStats, StravaStats, GoodreadsStats, GoogleSheetsStats, GoalStats):
        mocker.patch.object(collector, 'get_stats', return_value=[])
    mocker.patch.object(GoogleSheetsStats, 'get_stats', return_value=[stat])
    mocker.patch.object(WithingsStats, 'get_stats', side_effect=Exception('https://internal.example/secret-token'))


def test_failed_sources_reported_by_name_only(stub_collectors):
    from statsapp.blueprints.home.stat_collector import StatCollector

    stats, failed_sources = StatCollector.get_collected_stats(User.get_default_user())

    assert 'age' in stats
    assert failed_sources == ['Withings']


def test_data_endpoint_hides_exception_text(client, stub_collectors):
    resp = client.get('/data')

    body = resp.get_json()
    assert body['error_messages'] == ['Withings']
    assert b'secret-token' not in resp.data
