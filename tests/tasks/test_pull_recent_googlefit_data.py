import datetime

from statsapp.models.googlefit import GoogleFitData
from statsapp.models.user import User
from statsapp.tasks.pull_recent_googlefit_data import PullRecentGoogleFitData

def test_get_data_and_upsert(mock_googlefit_api):
    steps = 1
    distance = 2

    mock_googlefit_api.return_value = steps, distance
    user = User.get_default_user()
    date = datetime.date.today() # doesn't matter what the day is
    PullRecentGoogleFitData().get_data_and_upsert(date, user)

    data = GoogleFitData.query.all()
    assert len(data) == 1

    datum = data[0]
    assert datum.step_count == steps
    assert datum.distance_metres == distance
