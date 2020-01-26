import datetime

from statsapp import db


class WithingsData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User")
    date = db.Column(db.Date, nullable=False)
    weight_kg = db.Column(db.Float)
    __tableargs__ = (db.UniqueConstraint(user_id, date))


    def get_most_recent_weight(user):
        datum = WithingsData.query.filter_by(
            user=user
        ).filter(
            WithingsData.weight_kg.isnot(None)
        ).order_by(
            WithingsData.date.desc()
        ).limit(1).first()

        if datum:
            return datum.weight_kg

        return None

    def get_weight_datapoints_for_user(user):
        data = WithingsData.query.filter_by(
            user=user
        ).filter(
            WithingsData.weight_kg.isnot(None)
        ).all()

        date_weights = ((datum.date, datum.weight_kg) for datum in data)
        return date_weights

    def upsert(user, date, weight_kg):
        withings_obj = WithingsData.query.filter_by(
            user=user,
            date=date
        ).first()

        if not withings_obj:
            withings_obj = WithingsData()
            withings_obj.user = user
            withings_obj.date = date
        withings_obj.weight_kg = weight_kg

        db.session.add(withings_obj)
        db.session.commit()
        return withings_obj

    def get_data_for_year(user, year):
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)

        data = WithingsData.query.filter_by(
            user=user
        ).filter(
            WithingsData.date >= start_date
        ).filter(
            WithingsData.date <= end_date
        ).all()

        return data
