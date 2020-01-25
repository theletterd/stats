import datetime
import logging

from flask import Blueprint
from flask import redirect
from flask import request
from flask import url_for
from flask import flash
from flask import render_template
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from statsapp.models.googlefit import GoogleFitData
from statsapp.models.user import User
from statsapp.apis.googlefit import GoogleFitAPI
from statsapp.tools.util import chunks

user_app = Blueprint('user', __name__)


@user_app.route("/authorized_apps")
@login_required
def authorized_apps():
    strava_url = url_for("oauth.oauth_login", name='strava')
    gsheet_url = url_for("oauth.oauth_login", name='gsheet')
    goodreads_url = url_for("oauth.oauth_login", name='goodreads')
    googlefit_url = url_for("oauth.oauth_login", name='googlefit')
    withings_url = url_for("oauth.oauth_login", name='withings')
    missing_dates = GoogleFitData.days_missing(current_user)

    auth_urls = (
        ('Strava', strava_url),
        ('GSheet', gsheet_url),
        ('Goodreads', goodreads_url),
        ('Googlefit', googlefit_url),
        ('Withings', withings_url),
    )

    date_chunk_iterator = chunks(missing_dates, 20)
    date_chunks = [list(x) for x in date_chunk_iterator]
    context = dict(
        auth_urls=auth_urls,
        missing_dates=missing_dates,
        date_chunks=date_chunks
    )
    return render_template("authorised_apps.html", **context)


@user_app.route("/login", methods=['GET', 'POST'])
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
            return redirect(url_for("user.authorized_apps"))
        else:
            return render_template("login.html")
    else:
        if current_user.is_authenticated:
            return redirect(url_for("user.authorized_apps"))

        # show the login form,
        # TODO set CSRF cookie
        return render_template('login.html')


@user_app.route("/logout")
def logout():
    # log you out
    # set flash stuff
    flash("You're logged out, homie")
    logout_user()
    # redirect to homepage.
    return redirect(url_for('home.index'))


@user_app.route('/googlefit_date', methods=["POST"])
@login_required
def populate_googlefit_dates():
    dates = request.form.getlist("date")
    for date in dates:
        date = datetime.date.fromisoformat(date)
        missing_dates = GoogleFitData.days_missing(current_user)

        if date in missing_dates:
            try:
                step_count, distance_metres, weight_kg = GoogleFitAPI.get_stats_for_date(date, current_user)
                GoogleFitData.upsert(
                    current_user,
                    date,
                    step_count,
                    distance_metres,
                    weight_kg
                )
            except Exception as e:
                logging.exception(e)
    return ""

