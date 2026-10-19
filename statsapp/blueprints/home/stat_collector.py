import logging

from statsapp.models.stat import Stat
from statsapp.collectors.strava import StravaStats
from statsapp.collectors.goals import GoalStats
from statsapp.collectors.googlefit import GoogleFitStats
from statsapp.collectors.googlefit import GoogleFitYogaStats
from statsapp.collectors.goodreads import GoodreadsStats
from statsapp.collectors.gsheet import GoogleSheetsStats
from statsapp.collectors.withings import WithingsStats


class StatCollector(object):

    @staticmethod
    def get_collected_stats(user):
        stats = {}
        errors = []

        # can we run these concurrently?
        if not stats:
            stat_list = []

            # (source name shown to visitors if it fails, getter)
            stat_getters = [
                ("Google Fit", GoogleFitStats.get_stats),
                ("Google Fit yoga", GoogleFitYogaStats.get_stats),
                ("Strava", StravaStats.get_stats),
                ("Goodreads", GoodreadsStats.get_stats),
                ("Google Sheets", GoogleSheetsStats.get_stats),
                ("Goals", GoalStats.get_stats),
                ("Withings", WithingsStats.get_stats),
            ]

            for source, getter in stat_getters:
                try:
                    result = getter(user)
                    if type(result) is Stat:
                        stat_list.append(result)
                    else:
                        stat_list.extend(result)
                except Exception as e:
                    # the exception itself only goes to the logs, not the public page
                    errors.append(source)
                    logging.exception(e)

            for stat in stat_list:
                if stat:
                    stats[stat.stat_id] = stat._asdict()

        return stats, errors

