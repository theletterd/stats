from statsapp.models.stat import Stat
from statsapp.models.strava import StravaActivity
from statsapp.tools.util import today_pacific
from statsapp.tools.util import convert_metres_to_miles


class StravaStats(object):

    def get_stats(user):
        current_year = today_pacific().year
        prev_year = current_year - 1

        run_data = {}
        for year in (current_year, prev_year):
            runs = StravaActivity.get_activities_for_year(user, 'Run', year)
            run_data[year] = {
                'run_count': len(runs),
                'distance_run_metres': sum(run.distance_metres or 0 for run in runs)
            }

        distance_current_year = convert_metres_to_miles(run_data.get(current_year ,{}).get('distance_run_metres', 0))
        distance_last_year = convert_metres_to_miles(run_data.get(prev_year, {}).get('distance_run_metres', 0))

        constructed_stats = [
            Stat(
                stat_id='distance_run_current_year_miles',
                description='Distance this year (miles)',
                value=f"{distance_current_year:.2f}",
                notes=''
            ),
            Stat(
                stat_id='distance_run_prev_year_miles',
                description='Distance last year (miles)',
                value=f"{distance_last_year:.2f}",
                notes=''
            ),
            Stat(
                stat_id='run_count_current_year',
                description='Runs this year',
                value=run_data.get(current_year, {}).get('run_count', 0),
                notes=''
            ),
            Stat(
                stat_id='run_count_prev_year',
                description='Runs last year',
                value=run_data.get(prev_year, {}).get('run_count', 0),
                notes=''
            )
        ]

        return constructed_stats
