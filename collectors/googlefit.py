import datetime

from models import GoogleFitData
from models import Stat
from tools.util import convert_kg_to_lbs
from tools.util import convert_metres_to_miles


class GoogleFitStats(object):

    # so this is presumably where we should be collecting our stats from.
    def get_stats(user):
        return [
            GoogleFitStats.get_most_recent_weight(user),

        ]

    def get_stats_for_current_year(user):
        year = datetime.date.today().year
        stats = GoogleFitStats.get_stats_for_year(user, year)

        return [
            Stat(
                stat_id='g_step_count_current_year',
                description='Steps this year',
                value=stats['step_count']
            ),
            Stat(
                stat_id='g_distance_miles_current_year',
                description='Distance this year',
                value='{distance}'.format(distance=convert_metres_to_miles(stats['distance_metres']))
            ),
            Stat(
                stat_id='g_weight_lbs_min_current_year',
                description='Min Weight This Year',
                value='{weight:.1f}'.format(weight=convert_kg_to_lbs(stats['min_weight_kg']))
            ),
            Stat(
                stat_id='',
                description='',
                value=''
            ),
            Stat(
                stat_id='',
                description='',
                value=''
            )
        ]


    def _get_stats_for_year(user, year):
        data = GoogleFitData.get_data_for_year(user, year)

        steps = 0
        weights = []
        distance_metres = 0

        for datapoint in data:
            steps += datapoint.step_count
            distance_metres += datapoint.distance_metres

            if datapoint.weight_kg:
                weights.append(datapoint.weight_kg)

        if weights:
            # maybe not the most accurate measurement of average weight.
            avg_weight = sum(weights) / len(weights)
        else:
            avg_weight = None

        # from this, we can get min/max/average weight
        # and total steps, total distance

        return {
            'step_count': steps,
            'distance_metres': distance_metres,
            'min_weight_kg': min(weights),
            'max_weight_kg': max(weights),
            'avg_weight_kg': avg_weight
        }

    def get_most_recent_weight(user):
        weight_kg = GoogleFitData.get_most_recent_weight(user)

        if weight_kg:
            weight_lbs = convert_kg_to_lbs(weight_kg)
            return Stat(
                stat_id='weight_recent',
                description="Recent Weight (lbs)",
                value=f"{weight_lbs:.1f}"
            )

        return None

    def get_recent_stats():
        # steps yesterday
        # steps today

        # steps last week
        # steps this week so far

        # average weekly steps

        # distance yesterday
        # distance today

        # distance last week
        # distance this week
        # average weekly distance

        pass
