from flask import current_app

GSHEET_DOC_ID = current_app.config['GSHEET_DOC_ID']

from . import oauth
oauth.register(
    name='gsheet',
    api_base_url=f'https://sheets.googleapis.com/v4/spreadsheets/{GSHEET_DOC_ID}/',
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


class GoogleSheetsAPI(object):

    @classmethod
    def get_stat_data(klass):
        resp = oauth.gsheet.get('values/Overall%20stats!A%3AD')
        values = resp.json()['values']
        headers = values[0]

        stat_dicts = []
        for stat in values[1:]:
            if not stat:
                continue
            stat_dict = dict(zip(headers, stat))
            stat_dicts.append(stat_dict)

        return stat_dicts
