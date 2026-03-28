import requests

from statsapp.apis.goals import GoalsAPI
from statsapp.collectors.goals import GoalStats
from statsapp.models.user import User


def test_get_goals_data_returns_none_on_request_exception(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.exceptions.ConnectTimeout("timed out")

    monkeypatch.setattr("statsapp.apis.goals.requests.get", mock_get)

    assert GoalsAPI.get_goals_data() is None


def test_goal_stats_returns_empty_list_when_goals_unavailable(monkeypatch):
    monkeypatch.setattr("statsapp.collectors.goals.GoalsAPI.get_goals_data", lambda: None)

    user = User.get_default_user()
    assert GoalStats.get_stats(user) == []
