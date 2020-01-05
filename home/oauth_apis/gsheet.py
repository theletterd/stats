from flask import current_app

from models.stat import Stat

from . import oauth
oauth.register(
    name='gsheet',
    api_base_url='https://sheets.googleapis.com/v4/spreadsheets/12EaqvSuXoO2wiO80YKTrdlgsie0zwKc4t_esnNSPkdw/',
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
    def get_stats(klass):
        resp = oauth.gsheet.get('values/Overall%20stats!A%3AD')
        values = resp.json()['values']
        headers = values[0]

        stats = []
        for stat in values[1:]:
            if not stat:
                continue
            stat_dict = dict(zip(headers, stat))
            stats.append(Stat(**stat_dict))

        return stats
