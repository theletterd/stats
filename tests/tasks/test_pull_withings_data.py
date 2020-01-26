import datetime

from statsapp.models.withings import WithingsData
from statsapp.models.user import User
from statsapp.tasks.pull_withings_data import PullWithingsData

def test_get_data_and_upsert(mock_withings_api):
    weight = 3

    mock_withings_api.return_value = weight
    user = User.get_default_user()
    date = datetime.date.today() # doesn't matter what the day is
    PullWithingsData().get_data_and_upsert(date, user)

    data = WithingsData.query.all()
    assert len(data) == 1

    datum = data[0]
    assert datum.weight_kg == weight
