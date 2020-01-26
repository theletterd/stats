import datetime

from statsapp.models.googlefit import GoogleFitData
from statsapp.models.stat import Stat
from statsapp.tools.util import convert_metres_to_miles
from statsapp.tools.util import today_pacific

class GoogleFitStats(object):

    # so this is presumably where we should be collecting our stats from.
    def get_stats(user):
        return [
            *GoogleFitStats._get_stats_for_current_year(user),
            *GoogleFitStats._get_stats_for_prev_year(user),
            *GoogleFitStats._get_recent_stats(user)
        ]

    def _get_stats_for_current_year(user):
        year = today_pacific().year
        return GoogleFitStats._get_stats_for_year(user, year, "This year", "current_year")

    def _get_stats_for_prev_year(user):
        year = today_pacific().year - 1
        return GoogleFitStats._get_stats_for_year(user, year, "Last Year", "prev_year")

    def _get_stats_for_year(user, year, display_str, stat_str):
        data = GoogleFitData.get_data_for_year(user, year)

        step_count = 0
        distance_metres = 0

        for datapoint in data:
            step_count += datapoint.step_count
            distance_metres += datapoint.distance_metres

        return [
            Stat(
                stat_id=f'step_count_{stat_str}',
                description=f'Steps {display_str}',
                value='{steps:,}'.format(steps=step_count),
            ),
            Stat(
                stat_id=f'distance_miles_{stat_str}',
                description=f'Distance {display_str}',
                value='{distance:.0f}'.format(distance=convert_metres_to_miles(distance_metres)),
                notes="Includes running and walking"
            ),
        ]

    def _get_recent_stats(user):
        stats = []
        today = today_pacific()
        yesterday = today - datetime.timedelta(days=1)

        data_today = GoogleFitData.get_data_for_day(user, today)
        if data_today:
            stats.append(
                Stat(
                    stat_id='step_count_today',
                    description='Steps Today',
                    value='{steps:,}'.format(steps=data_today.step_count)
                )
            )
            stats.append(
                Stat(
                    stat_id=f'distance_miles_today',
                    description=f'Distance Today (miles)',
                    value='{distance:.2f}'.format(distance=convert_metres_to_miles(data_today.distance_metres)),
                    notes="Includes running and walking"
                )
            )

        data_yesterday = GoogleFitData.get_data_for_day(user, yesterday)
        if data_yesterday:
            stats.append(
                Stat(
                    stat_id='step_count_yesterday',
                    description='Steps Yesterday',
                    value='{steps:,}'.format(steps=data_yesterday.step_count),
                )
            )
            stats.append(
                Stat(
                    stat_id=f'distance_miles_yesterday',
                    description=f'Distance Yesterday(miles)',
                    value='{distance:.2f}'.format(distance=convert_metres_to_miles(data_yesterday.distance_metres)),
                    notes="Includes running and walking"
                )
            )

        return stats

