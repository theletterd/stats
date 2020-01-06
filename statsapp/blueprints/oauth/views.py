from flask import Blueprint
from flask import current_app
from flask_login import login_required
from flask import url_for
from flask import request
from flask import redirect
from flask_login import current_user

from statsapp.oauth_apis import oauth
from statsapp.models.oauth import OAuth1Token
from statsapp.models.oauth import OAuth2Token


oauth_app = Blueprint('oauth', __name__)

@oauth_app.route('/oauth/<string:name>/login')
@login_required
def oauth_login(name):
    redirect_uri = url_for('.authorize', _external=True, name=name)
    return oauth.__getattr__(name).authorize_redirect(redirect_uri)


@oauth_app.route('/authorize/<string:name>/')
@login_required
def authorize(name):
    token = oauth.__getattr__(name).authorize_access_token(oauth_verifier=request.args.get('authorize'))
    if name in current_app.config['OAUTH1_SERVICES']:
        model = OAuth1Token
    else:
        model = OAuth2Token
    model.upsert_token(name, token, current_user)
    return redirect('/')
