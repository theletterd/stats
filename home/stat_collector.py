import json

from pymemcache.client.base import Client

import config
from .oauth_apis import GoodreadsAPI
from .oauth_apis import GoogleSheetsAPI
from .oauth_apis import StravaAPI

memcached_client = Client(("localhost", config.MEMCACHED_PORT))


class StatCollector(object):

    @staticmethod
    def get_collected_stats():
        stats = {}
        errors = []

        # attempt to get stats from memcached
        stats = StatCollector._load_stats_from_memcached()

        # can we run these concurrently?
        if not stats:
            stat_list = []

            stat_getter_methods = [GoodreadsAPI.get_stats, GoogleSheetsAPI.get_stats, StravaAPI.get_stats]

            for getter in stat_getter_methods:
                try:
                    stat_list.extend(getter())
                except Exception as e:
                    errors.append(e)
                    print(e)

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


