from statsapp.collectors.googlefit import GoogleFitYogaStats
from statsapp.models.user import User


def test_get_stats_this_year_handles_no_sessions():
    user = User.get_default_user()

    stats = GoogleFitYogaStats.get_stats_this_year(user)

    stats_by_id = {stat.stat_id: stat for stat in stats}
    assert stats_by_id['yoga_sessions_current_year'].value == '0'
    assert stats_by_id['yoga_duration_current_year'].value == '0'
    assert stats_by_id['yoga_avg_duration_current_year'].value == '0'
