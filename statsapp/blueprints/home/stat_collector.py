import logging

from statsapp.models.stat import Stat
from statsapp.collectors.strava import StravaStats
from statsapp.collectors.goals import GoalStats
from statsapp.collectors.googlefit import GoogleFitStats
from statsapp.collectors.goodreads import GoodreadsStats
from statsapp.collectors.gsheet import GoogleSheetsStats


class StatCollector(object):

    @staticmethod
    def get_collected_stats(user):
        stats = {}
        errors = []

        # can we run these concurrently?
        if not stats:
            stat_list = []

            stat_getter_methods = [
                GoogleFitStats.get_stats,
                StravaStats.get_stats,
                GoodreadsStats.get_stats,
                GoogleSheetsStats.get_stats,
                GoalStats.get_stats,
            ]

            for getter in stat_getter_methods:
                try:
                    result = getter(user)
                    if type(result) is Stat:
                        stat_list.append(result)
                    else:
                        stat_list.extend(result)
                except Exception as e:
                    errors.append(e)
                    logging.exception(e)

            for stat in stat_list:
                if stat:
                    stats[stat.stat_id] = stat._asdict()

        return stats, errors

