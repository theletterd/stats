from statsapp.models.withings import WithingsData
from statsapp.models.stat import Stat
from statsapp.tools.util import convert_kg_to_lbs
from statsapp.tools.util import today_pacific

class WithingsStats(object):

    def get_stats(user):
        return [
            *WithingsStats._get_stats_for_current_year(user),
            *WithingsStats._get_stats_for_prev_year(user),
            WithingsStats._get_most_recent_weight(user),
        ]

    def _get_stats_for_current_year(user):
        year = today_pacific().year
        return WithingsStats._get_stats_for_year(user, year, "This year", "current_year")

    def _get_stats_for_prev_year(user):
        year = today_pacific().year - 1
        return WithingsStats._get_stats_for_year(user, year, "Last Year", "prev_year")


    def _get_stats_for_year(user, year, display_str, stat_str):
        data = WithingsData.get_data_for_year(user, year)
        if not data:
            return None

        weights = [datapoint.weight_kg for datapoint in data]

        avg_weight_kg = sum(weights) / len(weights)
        min_weight_kg = min(weights)
        max_weight_kg = max(weights)

        return [
            Stat(
                stat_id=f'weight_lbs_min_{stat_str}',
                description=f'Min Weight {display_str}',
                value='{weight:.1f}'.format(weight=convert_kg_to_lbs(min_weight_kg)),
                notes=''
            ),
            Stat(
                stat_id=f'weight_lbs_max_{stat_str}',
                description=f'Max Weight {display_str}',
                value='{weight:.1f}'.format(weight=convert_kg_to_lbs(max_weight_kg)),
                notes=''
            ),
            Stat(
                stat_id=f'weight_lbs_avg_{stat_str}',
                description=f'Avg Weight {display_str}',
                value='{weight:.1f}'.format(weight=convert_kg_to_lbs(avg_weight_kg)),
                notes=''
            )
        ]


    def _get_most_recent_weight(user):
        weight_kg = WithingsData.get_most_recent_weight(user)

        if weight_kg:
            weight_lbs = convert_kg_to_lbs(weight_kg)
            return Stat(
                stat_id='weight_lbs_recent',
                description="Recent Weight (lbs)",
                value=f"{weight_lbs:.1f}",
                notes=''
            )

        return None

