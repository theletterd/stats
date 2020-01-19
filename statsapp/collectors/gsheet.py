from statsapp import cache
from statsapp.models.stat import Stat
from statsapp.apis.gsheet import GoogleSheetsAPI


class GoogleSheetsStats(object):

    @cache.cached(key_prefix='gsheet_stats', timeout=60 * 60)
    def get_stats(user):
        # we're just reading stuff from my own spreadsheet. no need for a user
        # here, but for consistency's sake
        stat_dicts = GoogleSheetsAPI.get_stat_data()
        stats = []

        for stat_dict in stat_dicts:
            stats.append(Stat(**stat_dict))

        return stats

