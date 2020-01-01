from authlib.integrations.flask_client import OAuth

from .strava import StravaAPI
from .goodreads import GoodreadsAPI
from .gsheet import GoogleSheetsAPI

oauth = OAuth()
