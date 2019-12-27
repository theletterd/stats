import pprint
import json

from flask import Flask
from flask import jsonify
from flask import render_template
from pymemcache.client.base import Client

import config
import goodreads
import gsheet
import strava

memcached_client = Client(("localhost", config.MEMCACHED_PORT))

app = Flask(__name__)

@app.route("/")
def root():
    return render_template('index.html')

@app.route("/data")
def data():
    raw_stats = get_stats()
    stats = [
        {
            'stats': get_populated_stat_groups(raw_stats, config.MISC_STAT_GROUPS),
            'description': "Miscellaneous Stats",
            'stat_group': "misc_stats",
        },
        {
            'stats': get_populated_stat_groups(raw_stats, config.STEP_STAT_GROUPS),
            'description': 'Steps',
            'stat_group': "step_stats",
        },
        {
            'stats': get_populated_stat_groups(raw_stats, config.RUNNING_STAT_GROUPS),
            'description': 'Runs',
            'stat_group': "run_stats",
        },
        {
            'stats': get_populated_stat_groups(raw_stats, config.WEIGHT_STAT_GROUPS),
            'description' : 'Weight (lbs)',
            'stat_group': "weight_stats",
        },
        {
            'stats': get_populated_stat_groups(raw_stats, config.BOOK_STAT_GROUPS),
            'description' : 'Books',
            'stat_group': "book_stats",
        },
    ]
    return jsonify(stats)


def get_populated_stat_groups(raw_stats, stat_groups):
    return [[raw_stats[stat] for stat in stat_group] for stat_group in stat_groups]
            

def get_stats():
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
        
        stats.update(goodread_stats)
        stats.update(gsheet_stats)
        stats.update(running_stats)
        
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
    

if __name__ == '__main__':
    app.run()
