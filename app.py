import pprint
import json

from flask import Flask
from flask import jsonify
from flask import render_template

import config
from stat_collector import StatCollector

app = Flask(__name__)


ORDERED_STAT_GROUPS = [
    config.MISC_STAT_GROUPS,
    config.STEP_STAT_GROUPS,
    config.RUNNING_STAT_GROUPS,
    config.WEIGHT_STAT_GROUPS,
    config.BOOK_STAT_GROUPS,
]


@app.route("/")
def root():
    return render_template('index.html')


@app.route("/data")
def data():
    raw_stats, errors = StatCollector.get_collected_stats()

    # format the errors.
    error_messages = [str(e) for e in errors]

    stats = []

    for stat_group in ORDERED_STAT_GROUPS:
        populated_stats = _get_populated_stat_groups(raw_stats, stat_group['stat_groups'])
        if populated_stats:
            stats.append({
                    'stats': populated_stats,
                    'description': stat_group['description'],
                    'stat_group': stat_group['stat_group_id']
            })

    data = dict(
        stats=stats,
        error_messages=error_messages
    )

    return jsonify(data)


def _get_populated_stat_groups(raw_stats, stat_group):
    """
    Returns a list of lists, where each sub list is a list of stats for which
    we have data.
    """
    populated_stat_groups = []
    for stat_list in stat_group:
        populated_stat_group = []

        # only populate stats that we know we have.
        for stat in stat_list:
            populated_stat = raw_stats.get(stat)
            if populated_stat is not None:
                populated_stat_group.append(populated_stat)

        # if we end up with no stats in the group, let's not append it
        if populated_stat_group:
            populated_stat_groups.append(populated_stat_group)

    return populated_stat_groups
            


if __name__ == '__main__':
    app.run()
