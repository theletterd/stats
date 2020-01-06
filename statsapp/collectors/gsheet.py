from statsapp.models.stat import Stat
from statsapp.oauth_apis.gsheet import GoogleSheetsAPI


class GoogleSheetsStats(object):

    def get_stats(user):
        # we're just reading stuff from my own spreadsheet. no need for a user
        # here, but for consistency's sake
        stat_dicts = GoogleSheetsAPI.get_stat_data()
        stats = []

        for stat_dict in stat_dicts:
            stats.append(Stat(**stat_dict))

        return stats

