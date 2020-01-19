from flask_bcrypt import Bcrypt
from flask import current_app
from flask import Flask
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
cache = Cache()


def create_app(test_config=None):
    # if we're already in an app-context (e.g, in testing), don't create another one
    if current_app:
        return current_app

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('statsapp.config')

    if test_config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.update(test_config)


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
