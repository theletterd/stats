from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import flash

from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from .stat_collector import StatCollector
import config

from models import User
from models import OAuth1Token
from models import OAuth2Token

app = Blueprint('home', __name__)

from .oauth_apis import oauth


ORDERED_STAT_GROUPS = [
    config.MISC_STAT_GROUPS,
    config.STEP_STAT_GROUPS,
    config.RUNNING_STAT_GROUPS,
    config.WEIGHT_STAT_GROUPS,
    config.BOOK_STAT_GROUPS,
]

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/authorized_apps")
@login_required
def authorized_apps():
    strava_url = url_for("home.oauth_login", name='strava')
    gsheet_url = url_for("home.oauth_login", name='gsheet')
    goodreads_url = url_for("home.oauth_login", name='goodreads')
    context = dict(
        strava_url=strava_url,
        gsheet_url=gsheet_url,
        goodreads_url=goodreads_url
    )
    return render_template("authorised_apps.html", **context)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # do login stuff
        email = request.form.get("email")
        password = request.form.get("password")
        # do login stuff, set cookie, etc, redirect to homepage, show "HI THERE" thing
        user = User.check_login(email, password)
        # TODO use forms,
        if user:
            login_user(user)
            return redirect(url_for(".authorized_apps"))
        else:
            return render_template("login.html")

    else:
        # show the login form, set CSRF cookie
        return render_template('login.html')


@app.route("/logout")
def logout():
    # log you out
    # set flash stuff
    flash("You're logged out, homie")
    logout_user()
    # redirect to homepage.
    return redirect(url_for('.index'))


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


### oauth logins

@app.route('/oauth/<string:name>/login')
@login_required
def oauth_login(name):
    redirect_uri = url_for('home.authorize', _external=True, name=name)
    return oauth.__getattr__(name).authorize_redirect(redirect_uri)

@app.route('/authorize/<string:name>/')
@login_required
def authorize(name):
    print(request)
    token = oauth.__getattr__(name).authorize_access_token(oauth_verifier=request.args.get('authorize'))
    print(token)
    if name in current_app.config['OAUTH1_SERVICES']:
        model = OAuth1Token
    else:
        model = OAuth2Token
    model.upsert_token(name, token, current_user)
    return redirect('/')
