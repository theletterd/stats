import datetime

from models import GoogleFitData
from models import Stat
from tools.util import convert_kg_to_lbs
from tools.util import convert_metres_to_miles


class GoogleFitStats(object):

    # so this is presumably where we should be collecting our stats from.
    def get_stats(user):
        return [
            GoogleFitStats._get_most_recent_weight(user),
            *GoogleFitStats._get_stats_for_current_year(user),
            *GoogleFitStats._get_stats_for_prev_year(user),
            *GoogleFitStats._get_recent_stats(user)
        ]

    def _get_stats_for_current_year(user):
        year = datetime.date.today().year
        return GoogleFitStats._get_stats_for_year(user, year, "This year", "current_year")

    def _get_stats_for_prev_year(user):
        year = datetime.date.today().year - 1
        return GoogleFitStats._get_stats_for_year(user, year, "Last Year", "prev_year")

    def _get_stats_for_year(user, year, display_str, stat_str):
        data = GoogleFitData.get_data_for_year(user, year)

        step_count = 0
        weights = []
        distance_metres = 0

        for datapoint in data:
            step_count += datapoint.step_count
            distance_metres += datapoint.distance_metres

            if datapoint.weight_kg:
                weights.append(datapoint.weight_kg)

        if weights:
            # maybe not the most accurate measurement of average weight.
            avg_weight_kg = sum(weights) / len(weights)
        else:
            avg_weight_kg = None

        min_weight_kg = min(weights)
        max_weight_kg = max(weights)

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
            Stat(
                stat_id=f'weight_lbs_min_{stat_str}',
                description=f'Min Weight {display_str}',
                value='{weight:.1f}'.format(weight=convert_kg_to_lbs(min_weight_kg))
            ),
            Stat(
                stat_id=f'weight_lbs_max_{stat_str}',
                description=f'Max Weight {display_str}',
                value='{weight:.1f}'.format(weight=convert_kg_to_lbs(max_weight_kg))
            ),
            Stat(
                stat_id=f'weight_lbs_avg_{stat_str}',
                description=f'Avg Weight {display_str}',
                value='{weight:.1f}'.format(weight=convert_kg_to_lbs(avg_weight_kg))
            )
        ]

    def _get_most_recent_weight(user):
        weight_kg = GoogleFitData.get_most_recent_weight(user)

        if weight_kg:
            weight_lbs = convert_kg_to_lbs(weight_kg)
            return Stat(
                stat_id='weight_lbs_recent',
                description="Recent Weight (lbs)",
                value=f"{weight_lbs:.1f}"
            )

        return None

    def _get_recent_stats(user):
        stats = []
        today = datetime.date.today()
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

    def _get_other_stats(user):

        # steps last week
        # steps this week so far

        # average weekly steps

        # distance last week
        # distance this week
        # average weekly distance

        pass
