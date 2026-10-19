import datetime

import pytest

from statsapp.models.strava import StravaActivity
from statsapp.models.user import User

# statsapp.apis.strava reads app config at import time, so these modules are
# imported inside the tests, once the app fixture has set up a context.


def _activity(strava_id, start, sport_type='Run', distance=5000):
    return dict(strava_id=strava_id, sport_type=sport_type, start_date_local=start, distance_metres=distance)


@pytest.fixture
def mock_strava_api(mocker): # noqa
    return mocker.patch('statsapp.apis.strava.StravaAPI.get_activities')


def test_first_pull_fetches_everything(mock_strava_api):
    from statsapp.tasks.pull_strava_data import PullStravaData
    mock_strava_api.return_value = [
        _activity(1, datetime.datetime(2020, 1, 1)),
        _activity(2, datetime.datetime(2020, 1, 2), sport_type='Rowing'),
    ]
    user = User.get_default_user()

    PullStravaData(argv=[]).get_data_and_upsert(user)

    mock_strava_api.assert_called_once_with(user, after=None)
    assert StravaActivity.query.count() == 2


def test_later_pull_starts_before_most_recent_activity(mock_strava_api):
    from statsapp.tasks.pull_strava_data import OVERLAP
    from statsapp.tasks.pull_strava_data import PullStravaData
    user = User.get_default_user()
    latest = datetime.datetime(2020, 6, 1, 8, 0)
    StravaActivity.upsert(user, 1, 'Run', latest, 5000)
    mock_strava_api.return_value = [_activity(1, latest, distance=5200)]

    PullStravaData(argv=[]).get_data_and_upsert(user)

    mock_strava_api.assert_called_once_with(user, after=latest - OVERLAP)
    assert StravaActivity.query.count() == 1
    assert StravaActivity.query.first().distance_metres == 5200


def test_full_flag_ignores_stored_activities(mock_strava_api):
    from statsapp.tasks.pull_strava_data import PullStravaData
    user = User.get_default_user()
    StravaActivity.upsert(user, 1, 'Run', datetime.datetime(2020, 6, 1), 5000)
    mock_strava_api.return_value = []

    PullStravaData(argv=['--full']).get_data_and_upsert(user)

    mock_strava_api.assert_called_once_with(user, after=None)


def test_run_skips_users_without_strava_token(mock_strava_api):
    from statsapp.tasks.pull_strava_data import PullStravaData

    PullStravaData(argv=[]).run()

    mock_strava_api.assert_not_called()
