from flask_bcrypt import Bcrypt
from flask import current_app

from app import login_manager

bcrypt = Bcrypt()

from . import db

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

    @staticmethod
    def get_default_user():
        return User.query.filter_by(email=current_app.config['DEFAULT_USER_EMAIL']).first()

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

