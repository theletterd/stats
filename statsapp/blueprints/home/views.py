from collections import defaultdict
from collections import deque

from flask import Blueprint
from flask import jsonify
from flask import render_template

from . import view_config
from .stat_collector import StatCollector
from statsapp.apis.strava import StravaAPI
from statsapp.models.googlefit import GoogleFitData
from statsapp.models.googlefit import GoogleFitYoga
from statsapp.models.withings import WithingsData
from statsapp.models.user import User
from statsapp.tools.util import convert_kg_to_lbs

home_app = Blueprint('home', __name__)


ORDERED_STAT_GROUPS = [
    view_config.MISC_STAT_GROUPS,
    view_config.STEP_STAT_GROUPS,
    view_config.RUNNING_STAT_GROUPS,
    view_config.YOGA_STAT_GROUPS,
    view_config.WEIGHT_STAT_GROUPS,
    view_config.BOOK_STAT_GROUPS,
]


@home_app.route("/")
def index():
    return render_template('index.html')


@home_app.route("/data")
def data():
    user = User.get_default_user()
    raw_stats, errors = StatCollector.get_collected_stats(user)

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


@home_app.route("/weight")
def weight():
    user = User.get_default_user()
    weight_data = WithingsData.get_weight_datapoints_for_user(user)
    # that is an assumption. Let's do a sort
    earliest_date = sorted(weight_data, key=lambda x: x[0])[0][0]

    # TODO persist this in a DB
    strava_activity_data = StravaAPI.get_activity_data(user)

    #monthly_step_data = GoogleFitData.get_monthly_step_data(user, start_date=earliest_date)
    #formatted_step_data = [
    #    dict(x=date.replace(day=15).isoformat(), y=step_count) for date, step_count in monthly_step_data.items()
    #]

    weekly_step_data = GoogleFitData.get_weekly_step_data(user, start_date=earliest_date)
    formatted_step_data = [
        dict(x=date.isoformat(), y=step_count) for date, step_count in weekly_step_data.items()
    ]

    formatted_weight_data = [
        dict(x=date.isoformat(), y=convert_kg_to_lbs(weight_kg)) for date, weight_kg in weight_data
    ]

    # let's generated a moving average for weight
    sorted_weights = sorted(formatted_weight_data, key=lambda element: element['x'])
    window_size = 7
    window = deque(maxlen=window_size)
    weight_moving_average = []
    for datum in sorted_weights:
        window.append(datum)
        if len(window) != window_size:
            continue
        # get the sum of weights
        weight_sum = sum(map(lambda element: element['y'], window))
        mean_weight = weight_sum / window_size
        weight_date = window[int(window_size/2)]['x']
        # just use the mid date for now as the date thingy.
        weight_moving_average.append(dict(x=weight_date, y=mean_weight))


    # if I do >1 run/strava session a day, this screws up the chart.
    # we need to just extract the dates.
    run_distances = defaultdict(float)
    for date, distance_metres in strava_activity_data.get('Run', []):
        run_distances[date.date()] += distance_metres

    formatted_run_data = [
        dict(x=date.isoformat(), y=distance_metres) for date, distance_metres in run_distances.items() if date >= earliest_date
    ]

    # if I do >1 yoga session a day, this screws up the chart.
    # we need to just extract the dates.
    yoga_sessions = GoogleFitYoga.get_sessions(user, start_date=earliest_date)
    yoga_dates = set(session.date for session in yoga_sessions)
    formatted_yoga_data = [
        dict(x=yoga_date.isoformat(), y=1) for yoga_date in yoga_dates if yoga_date >= earliest_date
    ]
    context = {
        'weight_data': formatted_weight_data,
        'averaged_weight_data': weight_moving_average,
        'step_data': formatted_step_data,
        'run_data': formatted_run_data,
        'yoga_data': formatted_yoga_data,
    }
    return render_template('weight.html', **context)


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
