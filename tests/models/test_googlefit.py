from statsapp.models.user import User

def test_get_most_recent_weight():
    # set up a couple of weights
    user = User.get_default_user()
    print(user)


