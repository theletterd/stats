from flask_bcrypt import Bcrypt
from flask import current_app
from flask import Flask
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from . import db_util

csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
cache = Cache()


def create_app(config=None):
    # if we're already in an app-context (e.g, in testing), don't create another one
    if current_app:
        return current_app

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('statsapp.config')
    app.config.update(db_util.get_db_config())
    app.config.update(db_util.get_cache_config())

    if config:
        app.config.update(config)
    else:
        # read from the instance config
        app.config.from_pyfile('config.py')


    with app.app_context():
        csrf.init_app(app)

        db.init_app(app)
        db.create_all()

        bcrypt.init_app(app)
        cache.init_app(app)
        login_manager.init_app(app)

        # does it make sense to add the oauth library here?
        from statsapp.apis import oauth
        oauth.init_app(app)

        from statsapp import blueprints
        app.register_blueprint(blueprints.home_app)
        app.register_blueprint(blueprints.oauth_app)
        app.register_blueprint(blueprints.user_app)

    return app
