import json
import logging

from pymemcache.client.base import Client

import config
from models.stat import Stat
from oauth_apis.gsheet import GoogleSheetsAPI
from collectors.strava import StravaStats
from collectors.googlefit import GoogleFitStats
from collectors.goodreads import GoodreadsStats

memcached_client = Client(("localhost", config.MEMCACHED_PORT))


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
            stat_list = [
                *GoogleFitStats.get_stats(user),
                 *StravaStats.get_stats(user),
                 *GoodreadsStats.get_stats(user)
            ]

            stat_getter_methods = [
                GoogleSheetsAPI.get_stats,
            ]

            for getter in stat_getter_methods:
                try:
                    result = getter()
                    if type(result) is Stat:
                        stat_list.append(result)
                    else:
                        stat_list.extend(result)
                except Exception as e:
                    errors.append(e)
                    logging.exception(e)

            for stat in stat_list:
                stats[stat.stat_id] = stat._asdict()

        # attempt to push stats back to memcached
        StatCollector._dump_stats_to_memcached(stats)
        return stats, errors

    @staticmethod
    def _load_stats_from_memcached():
        stats = {}
        try:
            stats = json.loads(memcached_client.get(config.MEMCACHED_STATS_KEY))
        except Exception as e:
            print(e)

        return stats

    @staticmethod
    def _dump_stats_to_memcached(stats):
        try:
            memcached_client.set(
                config.MEMCACHED_STATS_KEY,
                json.dumps(stats),
                expire=60 * 15
            )
        except Exception as e:
            print(e)
            pass


