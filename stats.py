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

    stat_groups = [
        config.MISC_STAT_GROUPS,
        config.STEP_STAT_GROUPS,
        config.RUNNING_STAT_GROUPS,
        config.WEIGHT_STAT_GROUPS,
        config.BOOK_STAT_GROUPS,
    ]

    stats = []

    for stat_group in stat_groups:
        stats.append({
                'stats': get_populated_stat_groups(raw_stats, stat_group['stat_groups']),
                'description': stat_group['description'],
                'stat_group': stat_group['stat_group_id']
        })
    return jsonify(stats)


def get_populated_stat_groups(raw_stats, stat_groups):
    populated_stat_groups = []
    for stat_group in stat_groups:
        populated_stat_group = []

        # only populate stats that we know we have.
        for stat in stat_group:
            populated_stat = raw_stats.get(stat)
            if populated_stat is not None:
                populated_stat_group.append(populated_stat)

        # if we end up with no stats in the group, let's not append it
        if populated_stat_group:
            populated_stat_groups.append(populated_stat_group)

    return populated_stat_groups
            

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
    

if __name__ == '__main__':
    app.run()
