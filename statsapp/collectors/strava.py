from statsapp import cache
from statsapp.models.stat import Stat
from statsapp.apis.strava import StravaAPI
from statsapp.tools.util import today_pacific
from statsapp.tools.util import convert_metres_to_miles


class StravaStats(object):

    @cache.cached(key_prefix="running_stats", timeout=60 * 15)
    def get_stats(user):
        runs = StravaAPI.get_run_data(user)

        run_data = {}
        for run_date, distance_metres in runs:

            if run_date.year not in run_data:
                run_data[run_date.year] = {
                    'run_count': 0,
                    'distance_run_metres': 0
                }

            run_data[run_date.year]['run_count'] += 1
            run_data[run_date.year]['distance_run_metres'] += distance_metres


        # construct stats
        current_year = today_pacific().year
        prev_year = current_year - 1

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
