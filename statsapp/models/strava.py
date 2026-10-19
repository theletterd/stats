import datetime

from statsapp import db


class StravaActivity(db.Model):
    """
    One row per Strava activity, of any sport type. Keyed on Strava's own
    activity id so re-pulling the same activities just updates them.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User")
    strava_id = db.Column(db.BigInteger, nullable=False)
    sport_type = db.Column(db.String(40), nullable=False)
    start_date_local = db.Column(db.DateTime, nullable=False)
    distance_metres = db.Column(db.Float)
    __table_args__ = (db.UniqueConstraint('user_id', 'strava_id'),)

    def get_activities(user, sport_type, start_date=None, end_date=None):
        query = StravaActivity.query.filter_by(
            user=user,
            sport_type=sport_type
        )

        if start_date:
            query = query.filter(
                StravaActivity.start_date_local >= datetime.datetime.combine(start_date, datetime.time.min)
            )

        if end_date:
            query = query.filter(
                StravaActivity.start_date_local <= datetime.datetime.combine(end_date, datetime.time.max)
            )

        return query.order_by(
            StravaActivity.start_date_local
        ).all()

    def get_activities_for_year(user, sport_type, year):
        return StravaActivity.get_activities(
            user,
            sport_type,
            start_date=datetime.date(year, 1, 1),
            end_date=datetime.date(year, 12, 31)
        )

    def get_most_recent_start(user):
        datum = StravaActivity.query.filter_by(
            user=user
        ).order_by(
            StravaActivity.start_date_local.desc()
        ).first()

        if datum:
            return datum.start_date_local

        return None

    def upsert(user, strava_id, sport_type, start_date_local, distance_metres):
        activity = StravaActivity.query.filter_by(
            user=user,
            strava_id=strava_id
        ).first()

        if not activity:
            activity = StravaActivity()
            activity.user = user
            activity.strava_id = strava_id
        activity.sport_type = sport_type
        activity.start_date_local = start_date_local
        activity.distance_metres = distance_metres

        db.session.add(activity)
        db.session.commit()
        return activity
