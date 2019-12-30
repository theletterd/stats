from pymemcache.client.base import Client

import config
import goodreads
import gsheet
import strava



memcached_client = Client(("localhost", config.MEMCACHED_PORT))



class StatCollector(object):

    @staticmethod
    def get_collected_stats():
        stats = {}

        # attempt to get stats from memcached
        try:
            stats = json.loads(memcached_client.get(config.MEMCACHED_STATS_KEY))
        except Exception as e:
            pass

        # can we run these concurrently?
        if not stats:
            goodread_stats = goodreads.get_stats()
            gsheet_stats = gsheet.get_stats()
            running_stats = strava.get_stats()

            for stat_list in goodread_stats, gsheet_stats, running_stats:
                for stat in stat_list:
                    stats[stat.stat_id] = stat._asdict()

        # attempt to push stats back to memcached
        try:
            memcached_client.set(
                config.MEMCACHED_STATS_KEY,
                json.dumps(stats),
                expire=60 * 15
            )
        except:
            pass

        return stats
    
