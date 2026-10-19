import datetime
from unittest import mock

from statsapp.models.user import User


def _raw_activity(strava_id):
    return {'id': strava_id, 'sport_type': 'Run', 'start_date_local': '2020-01-01T07:00:00Z', 'distance': 1000.0}


def test_get_activities_follows_pages(mocker): # noqa
    # imported here because statsapp.apis.strava reads app config at import time
    from statsapp.apis.strava import StravaAPI

    mocker.patch('statsapp.apis.strava.fetch_token', return_value={})
    mocker.patch.object(StravaAPI, 'PAGE_SIZE', 2)
    mock_oauth = mocker.patch('statsapp.apis.strava.oauth')
    pages = [[_raw_activity(1), _raw_activity(2)], [_raw_activity(3)]]
    mock_oauth.strava.get.side_effect = [mock.Mock(json=mock.Mock(return_value=page)) for page in pages]

    after = datetime.datetime(2020, 1, 1)
    activities = StravaAPI.get_activities(User.get_default_user(), after=after)

    assert [a['strava_id'] for a in activities] == [1, 2, 3]
    assert activities[0]['start_date_local'] == datetime.datetime(2020, 1, 1, 7, 0)
    assert mock_oauth.strava.get.call_count == 2
    pages_requested = [call.kwargs['params']['page'] for call in mock_oauth.strava.get.call_args_list]
    assert pages_requested == [1, 2]
    assert mock_oauth.strava.get.call_args.kwargs['params']['after'] == 1577836800
