from flask import Flask
from flask_login import LoginManager

import secret

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.secret_key = secret.FLASK_SECRET_KEY

    # TODO move to a config somewhere
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./sqlite_database'

    from models import db

    with app.app_context():
        db.init_app(app)
        db.create_all()

    from models import bcrypt
    bcrypt.init_app(app)

    login_manager.init_app(app)


    from home import home_app
    app.register_blueprint(home_app)

    return app


def run_app():
    app = create_app()
    app.run()
