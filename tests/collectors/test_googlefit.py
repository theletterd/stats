import datetime

from statsapp.collectors.googlefit import GoogleFitStats
from statsapp.collectors.googlefit import GoogleFitYogaStats
from statsapp.models.googlefit import GoogleFitData
from statsapp.tools.util import today_pacific
from statsapp.models.user import User


def test_get_stats_this_year_handles_no_sessions():
    user = User.get_default_user()

    stats = GoogleFitYogaStats.get_stats_this_year(user)

    stats_by_id = {stat.stat_id: stat for stat in stats}
    assert stats_by_id['yoga_sessions_current_year'].value == '0'
    assert stats_by_id['yoga_duration_current_year'].value == '0'
    assert stats_by_id['yoga_avg_duration_current_year'].value == '0'


def test_step_stats_omitted_for_years_without_data():
    user = User.get_default_user()
    this_year = today_pacific().year
    GoogleFitData.upsert(user, datetime.date(this_year, 1, 1), 1000, 800)

    stats = GoogleFitStats.get_stats(user)

    stat_ids = {stat.stat_id for stat in stats}
    assert 'step_count_current_year' in stat_ids
    assert 'step_count_prev_year' not in stat_ids
