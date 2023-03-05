import datetime
from statsapp.models.withings import WithingsData
from statsapp.models.user import User
from statsapp import db

def test_get_most_recent_weight():
    # set up a couple of weights
    user = User.get_default_user()
    recent_data = WithingsData(user=user, date=datetime.date(2020, 1, 1))
    weight = WithingsData.get_most_recent_weight(user)
    assert weight is None

    past_data = WithingsData(user=user, date=datetime.date(2019, 1, 1), weight_kg=5)
    db.session.add(recent_data)
    db.session.add(past_data)
    db.session.commit()

    weight = WithingsData.get_most_recent_weight(user)
    assert weight == 5
