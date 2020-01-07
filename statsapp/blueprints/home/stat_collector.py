import json
import logging

from flask import current_app
from pymemcache.client.base import Client

from statsapp.models.stat import Stat
from statsapp.collectors.strava import StravaStats
from statsapp.collectors.googlefit import GoogleFitStats
from statsapp.collectors.goodreads import GoodreadsStats
from statsapp.collectors.gsheet import GoogleSheetsStats

memcached_client = Client(("localhost", current_app.config['MEMCACHED_PORT']))


class StatCollector(object):

    @staticmethod
    def get_collected_stats(user):
        stats = {}
        errors = []

        # attempt to get stats from memcached
        # TODO we can probably does this on a per-stat (or per type?) basis, instead of for everything?
        # also by user.... yeesh.
        # also we need a way to hard-refresh.
        stats = StatCollector._load_stats_from_memcached()

        # can we run these concurrently?
        if not stats:
            stat_list = []

            stat_getter_methods = [
                GoogleFitStats.get_stats,
                StravaStats.get_stats,
                GoodreadsStats.get_stats,
                GoogleSheetsStats.get_stats,
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

        # attempt to push stats back to memcached
        StatCollector._dump_stats_to_memcached(stats)
        return stats, errors

    # TODO make these into a decorator
    @staticmethod
    def _load_stats_from_memcached():
        stats = {}
        try:
            stats = json.loads(memcached_client.get(current_app.config['MEMCACHED_STATS_KEY']))
        except Exception as e:
            print(e)

        return stats

    @staticmethod
    def _dump_stats_to_memcached(stats):
        try:
            memcached_client.set(
                current_app.config['MEMCACHED_STATS_KEY'],
                json.dumps(stats),
                expire=60 * 15
            )
        except Exception as e:
            print(e)
            pass


