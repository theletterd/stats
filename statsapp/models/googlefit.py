import datetime

from statsapp.tools.util import today_pacific
from statsapp.tools import util
from statsapp import db


class GoogleFitData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User")
    date = db.Column(db.Date, nullable=False)
    step_count = db.Column(db.Integer)
    distance_metres = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    __tableargs__ = (db.UniqueConstraint(user_id, date))

    def days_missing(user):
        # we should have days for all of the previous year, and
        # all days this year so far.
        end_date = today_pacific()

        start_date = datetime.date(end_date.year - 1, 1, 1)
        expected_dates = set(util.get_dates_between(start_date, end_date))

        # ok now we query the database for all the dates that we have
        # We could probably filter by start/end dates here
        data_objs = GoogleFitData.query.filter_by(
            user=user
            ).all()

        for data_obj in data_objs:
            if data_obj.date in expected_dates:
                expected_dates.remove(data_obj.date)
        return expected_dates

    def get_most_recent_weight(user):
        datum = GoogleFitData.query.filter_by(
            user=user
        ).filter(
            GoogleFitData.weight_kg is not None
        ).order_by(
            GoogleFitData.date.desc()
        ).limit(1).first()

        if datum:
            return datum.weight_kg

        return None

    def get_data_for_year(user, year):
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)

        data = GoogleFitData.query.filter_by(
            user=user
        ).filter(
            GoogleFitData.date >= start_date
        ).filter(
            GoogleFitData.date <= end_date
        ).all()

        return data

    def get_data_for_day(user, date):
        data = GoogleFitData.query.filter_by(
            user=user,
            date=date
        ).first()

        return data

    def upsert(user, date, step_count, distance_metres, weight_kg):
        fit_obj = GoogleFitData.query.filter_by(
            user=user,
            date=date
        ).first()

        if not fit_obj:
            fit_obj = GoogleFitData()
            fit_obj.user = user
            fit_obj.date = date
        fit_obj.step_count = step_count
        fit_obj.weight_kg = weight_kg
        fit_obj.distance_metres = distance_metres

        db.session.add(fit_obj)
        db.session.commit()
        return fit_obj
