from authlib.integrations.flask_client import OAuth
from models import OAuth2Token
oauth = OAuth(fetch_token=OAuth2Token.fetch_token, update_token=OAuth2Token.update_token)
oauth.register('strava')
