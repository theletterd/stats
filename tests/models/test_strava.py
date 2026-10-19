import datetime

from statsapp.models.strava import StravaActivity
from statsapp.models.user import User


def test_upsert_updates_existing_activity():
    user = User.get_default_user()
    start = datetime.datetime(2020, 5, 1, 7, 30)

    StravaActivity.upsert(user, 123, 'Run', start, 5000)
    StravaActivity.upsert(user, 123, 'Run', start, 5100)

    activities = StravaActivity.query.all()
    assert len(activities) == 1
    assert activities[0].distance_metres == 5100


def test_get_activities_for_year_filters_by_year_and_sport():
    user = User.get_default_user()
    StravaActivity.upsert(user, 1, 'Run', datetime.datetime(2019, 12, 31, 23, 0), 1000)
    StravaActivity.upsert(user, 2, 'Run', datetime.datetime(2020, 1, 1, 0, 30), 2000)
    StravaActivity.upsert(user, 3, 'Run', datetime.datetime(2020, 12, 31, 23, 0), 3000)
    StravaActivity.upsert(user, 4, 'Rowing', datetime.datetime(2020, 6, 1, 8, 0), 4000)

    runs = StravaActivity.get_activities_for_year(user, 'Run', 2020)
    assert [run.strava_id for run in runs] == [2, 3]


def test_get_most_recent_start():
    user = User.get_default_user()
    assert StravaActivity.get_most_recent_start(user) is None

    StravaActivity.upsert(user, 1, 'Run', datetime.datetime(2020, 1, 1), 1000)
    StravaActivity.upsert(user, 2, 'Rowing', datetime.datetime(2020, 3, 1), 1000)

    assert StravaActivity.get_most_recent_start(user) == datetime.datetime(2020, 3, 1)
