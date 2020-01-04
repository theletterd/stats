import json
import logging

from pymemcache.client.base import Client

import config
from models import Stat
from .oauth_apis.goodreads import GoodreadsAPI
from .oauth_apis.gsheet import GoogleSheetsAPI
from .oauth_apis.strava import StravaAPI
from collectors.googlefit import GoogleFitStats

memcached_client = Client(("localhost", config.MEMCACHED_PORT))


class StatCollector(object):

    @staticmethod
    def get_collected_stats(user):
        stats = {}
        errors = []

        # attempt to get stats from memcached
        stats = StatCollector._load_stats_from_memcached()

        # can we run these concurrently?
        if not stats:
            stat_list = [
                GoogleFitStats.get_most_recent_weight(user)
            ]

            stat_getter_methods = [
                GoogleSheetsAPI.get_stats,
                StravaAPI.get_stats,
            ]
            stat_getter_methods.extend(GoodreadsAPI.get_stat_getters())
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


