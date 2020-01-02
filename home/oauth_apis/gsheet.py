import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import current_app

from .exceptions import stat_exception_override

GSHEET_JSON_KEYFILE = current_app.config['GSHEET_JSON_KEYFILE']

from models import Stat

from . import oauth
oauth.register(
    name='gsheet',
    api_base_url='',
    # used to get a user's permissions
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    authorize_params={
        'scope': 'https://www.googleapis.com/auth/spreadsheets.readonly',
        'access_type': 'offline'
    },
    # used for getting the token
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params={
        'client_id': current_app.config['GSHEET_CLIENT_ID'],
        'client_secret': current_app.config['GSHEET_CLIENT_SECRET'],
    }
)

# use creds to create a client to interact with the Google Drive API
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive",]

creds = ServiceAccountCredentials.from_json_keyfile_dict(GSHEET_JSON_KEYFILE, scope)
client = gspread.authorize(creds)

class GoogleSheetsAPI(object):

    @classmethod
    @stat_exception_override("google sheets")
    def get_stats(klass):
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        client.login()
        sheet = client.open("Stats").sheet1

        sheet_stats = sheet.get_all_records()

        stats = []
        for stat in sheet_stats:
            if stat.get("stat_id"):
                stats.append(
                    Stat(
                        stat_id=stat['stat_id'],
                        description=stat['description'],
                        value=stat['value'],
                        notes=stat['notes']
                ))
        return stats
