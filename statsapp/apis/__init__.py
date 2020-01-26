from authlib.integrations.flask_client import OAuth

from statsapp.models.oauth import fetch_token, OAuth2Token

oauth = OAuth(fetch_token=fetch_token, update_token=OAuth2Token.update_token)

from .withings import WithingsAPI
