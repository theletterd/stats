from authlib.integrations.flask_client import OAuth
from models import fetch_token, OAuth2Token
oauth = OAuth(fetch_token=fetch_token, update_token=OAuth2Token.update_token)
oauth.register('strava')
oauth.register('gsheet')
oauth.register('goodreads')
