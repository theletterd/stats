from flask import current_app

from statsapp import config
from statsapp import db
from statsapp import db_util
from statsapp.models.user import User


class OAuth1Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    oauth_token = db.Column(db.String(200), nullable=False)
    oauth_token_secret = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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


def fetch_token(name, user=None):
    if user is None:
        user = User.get_default_user()

    if name in config.OAUTH1_SERVICES:
        model = OAuth1Token
    else:
        model = OAuth2Token

    token = model.query.filter_by(
        name=name,
        user=user
    ).first()
    if token:
        return token.to_token()
    else:
        return None
