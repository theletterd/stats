import json
import logging

from pymemcache.client.base import Client

import config
from apis import goodreads
from apis import gsheet
from apis import strava

memcached_client = Client(("localhost", config.MEMCACHED_PORT))


class StatCollector(object):

    @staticmethod
    def get_collected_stats():
        stats = {}

        # attempt to get stats from memcached
        stats = StatCollector._load_stats_from_memcached()

        # can we run these concurrently?
        if not stats:
            goodread_stats = goodreads.get_stats()
            gsheet_stats = gsheet.get_stats()
            running_stats = strava.get_stats()

            for stat_list in goodread_stats, gsheet_stats, running_stats:
                for stat in stat_list:
                    stats[stat.stat_id] = stat._asdict()

        # attempt to push stats back to memcached
        StatCollector._dump_stats_to_memcached(stats)

        return stats

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

    
