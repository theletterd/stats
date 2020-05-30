from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import render_template

from .stat_collector import StatCollector
from statsapp.apis.strava import StravaAPI
from statsapp.models.googlefit import GoogleFitData
from statsapp.models.withings import WithingsData
from statsapp.models.user import User
from statsapp.tools.util import convert_kg_to_lbs

home_app = Blueprint('home', __name__)


ORDERED_STAT_GROUPS = [
    current_app.config['MISC_STAT_GROUPS'],
    current_app.config['STEP_STAT_GROUPS'],
    current_app.config['RUNNING_STAT_GROUPS'],
    current_app.config['YOGA_STAT_GROUPS'],
    current_app.config['WEIGHT_STAT_GROUPS'],
    current_app.config['BOOK_STAT_GROUPS'],
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
    runs = StravaAPI.get_run_data(user)

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

    formatted_run_data = [
        dict(x=date.date().isoformat(), y=1) for date, distance_metres in runs if date.date() >= earliest_date
    ]

    context = {
        'weight_data': formatted_weight_data,
        'step_data': formatted_step_data,
        'run_data': formatted_run_data,
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


