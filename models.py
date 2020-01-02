from collections import namedtuple

from flask import current_app
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


class OAuth1Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    oauth_token = db.Column(db.String(200), nullable=False)
    oauth_token_secret = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User")

    def to_token(self):
        return dict(
            oauth_token=self.oauth_token,
            oauth_token_secret=self.oauth_token_secret,
        )

    @staticmethod
    def upsert_token(name, token, user):
        # let's see if there's already a token.
        token_obj = OAuth1Token.query.filter_by(
            name=name,
            user=user
        ).first()

        if not token_obj:
            token_obj = OAuth1Token()
            token_obj.name = name
            token_obj.user = user
        token_obj.oauth_token = token['oauth_token']
        token_obj.oauth_token_secret = token['oauth_token_secret']

        db.session.add(token_obj)
        db.session.commit()


class OAuth2Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    token_type = db.Column(db.String(40), nullable=False)
    access_token = db.Column(db.String(200), nullable=False)
    refresh_token = db.Column(db.String(200), nullable=False)
    expires_at = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User")

    def to_token(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )

    @staticmethod
    def upsert_token(name, token, user):
        # let's see if there's already a token.
        token_obj = OAuth2Token.query.filter_by(
            name=name,
            user=user
        ).first()

        if not token_obj:
            token_obj = OAuth2Token()
            token_obj.name = name
            token_obj.token_type = token['token_type']
            token_obj.user = user
        token_obj.access_token = token['access_token']
        token_obj.refresh_token = token.get('refresh_token')
        token_obj.expires_at = token['expires_at']

        db.session.add(token_obj)
        db.session.commit()


    @staticmethod
    def update_token(name, token, refresh_token=None, access_token=None):
        if refresh_token:
            item = OAuth2Token.query.filter_by(name=name, refresh_token=refresh_token).first()
        elif access_token:
            item = OAuth2Token.query.filter_by(name=name, access_token=access_token).first()
        else:
            return

        # update old token
        item.access_token = token['access_token']
        item.refresh_token = token.get('refresh_token')
        item.expires_at = token['expires_at']
        db.session.add(item)
        db.session.commit()


def fetch_token(name):
    default_user = User.get_default_user()
    if not default_user:
        return None
    if name in current_app.config['OAUTH1_SERVICES']:
        model = OAuth1Token
    else:
        model = OAuth2Token

    token = model.query.filter_by(
        name=name,
        user=default_user
    ).first()
    if token:
        return token.to_token()
    else:
        return None

# NOTE:
# When querying in ipython, you can do:
"""
from app import create_app
app = create_app()
with app.app_context():
     u = User.query.get(1)
"""
