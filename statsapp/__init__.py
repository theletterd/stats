from flask_bcrypt import Bcrypt
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('statsapp.config')
    app.config.from_pyfile('config.py')

    with app.app_context():
        db.init_app(app)
        db.create_all()

        bcrypt.init_app(app)
        login_manager.init_app(app)

        # does it make sense to add the oauth library here?
        from statsapp.oauth_apis import oauth
        oauth.init_app(app)

        from statsapp import blueprints
        app.register_blueprint(blueprints.home_app)
        app.register_blueprint(blueprints.oauth_app)
        app.register_blueprint(blueprints.user_app)

    return app
