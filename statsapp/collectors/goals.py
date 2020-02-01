from statsapp import cache
from statsapp.apis.goals import GoalsAPI
from statsapp.models.stat import Stat

class GoalStats(object):

    @cache.cached(key_prefix="goal_completion", timeout=60 * 60 * 24)
    def get_stats(user):
        # we don't use user here, it's just for consistency's sake
        goal_data = GoalsAPI.get_goals_data()

        year_completion = goal_data['overall_completion']

        return [
            Stat(
                stat_id='goal_completion',
                description='Goal Completion',
                value=f'{year_completion:.0f}%',
                notes='Goal data read from https://goals.theletterd.co.uk'
            )
        ]

