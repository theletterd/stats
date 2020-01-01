from collections import namedtuple

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

Stat = namedtuple(
    'Stat',
    (
        'stat_id',
        'description',
        'value',
        'notes',
    ),
    defaults=('',)
)

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

    @staticmethod
    def check_login(email, password):
        user = User.query.filter_by(email=email).first()
        if not user:
            return False

        stored_password_hash = user.password_hash

        return bcrypt.check_password_hash(stored_password_hash, password.encode("utf-8"))

    @staticmethod
    def create_user(email, password):
        # I only expect this to be called from the command line.
        hashed_password = bcrypt.generate_password_hash(
            password.encode("utf-8")
        )

        user = User(email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        return user
