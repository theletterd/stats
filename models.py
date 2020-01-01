from collections import namedtuple

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from app import login_manager

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

        if bcrypt.check_password_hash(stored_password_hash, password.encode("utf-8")):
            return user

        return None

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


    ### following methods are for flask-login compliance

    @login_manager.user_loader
    def get_user(user_id):
        return User.query.get(user_id)


    @property
    def is_active(self):
        return True # we don't have any concept of inactive users

    @property
    def is_authenticated(self):
        # this seems... wrong?
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)



# NOTE:
# When querying in ipython, you can do:
# from app import create_app
# app = create_app()
# with app.app_context():
#     u = User.query.get(1)
