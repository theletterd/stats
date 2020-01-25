from statsapp.models.oauth import fetch_token
from . import oauth


oauth.register(
    name='withings',
    api_base_url='',
    authorize_url='https://account.withings.com/oauth2_user/authorize2',
    authorize_params={'scope':'user.metrics'},
    access_token_url='https://account.withings.com/oauth2/token',
)


class WithingsAPI(object):

    def get_weight_data(user):
        token = fetch_token('withings', user)

        resp = oauth.withings.get('', token=token)
        resp
        return 3
