import datetime

from statsapp import db
from statsapp.collectors.googlefit import GoogleFitYogaStats
from statsapp.collectors.strava import StravaStats
from statsapp.collectors.withings import WithingsStats
from statsapp.models.googlefit import GoogleFitYoga
from statsapp.models.strava import StravaActivity
from statsapp.models.user import User
from statsapp.models.withings import WithingsData
from statsapp.tools.util import today_pacific


def _by_id(stats):
    return {stat.stat_id: stat for stat in stats if stat}


def test_strava_stats_count_runs_only():
    user = User.get_default_user()
    year = today_pacific().year
    StravaActivity.upsert(user, 1, 'Run', datetime.datetime(year, 1, 1, 8), 1609)
    StravaActivity.upsert(user, 2, 'Run', datetime.datetime(year - 1, 6, 1, 8), 3218)
    StravaActivity.upsert(user, 3, 'Rowing', datetime.datetime(year, 1, 2, 8), 5000)

    stats = _by_id(StravaStats.get_stats(user))

    assert stats['run_count_current_year'].value == 1
    assert stats['run_count_prev_year'].value == 1
    assert stats['distance_run_current_year_miles'].value == '1.00'
    assert stats['distance_run_prev_year_miles'].value == '2.00'


def test_yoga_stats_with_no_sessions():
    stats = _by_id(GoogleFitYogaStats.get_stats(User.get_default_user()))
    assert stats['yoga_sessions_current_year'].value == '0'
    assert stats['yoga_avg_duration_current_year'].value == '0'


def test_withings_stats_with_no_data_last_year():
    user = User.get_default_user()
    WithingsData.upsert(user, today_pacific(), 80)

    stats = _by_id(WithingsStats.get_stats(user))

    assert 'weight_lbs_avg_current_year' in stats
    assert 'weight_lbs_avg_prev_year' not in stats


def test_yoga_get_sessions_respects_start_date():
    user = User.get_default_user()
    GoogleFitYoga.upsert(user, datetime.date(2020, 1, 1), 1, 600)
    GoogleFitYoga.upsert(user, datetime.date(2020, 3, 1), 2, 600)

    sessions = GoogleFitYoga.get_sessions(user, start_date=datetime.date(2020, 2, 1))

    assert [s.date for s in sessions] == [datetime.date(2020, 3, 1)]
