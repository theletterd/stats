from flask import Flask
from flask_login import LoginManager

login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    with app.app_context():
        from models import db
        db.init_app(app)
        db.create_all()

        from models.user import bcrypt
        bcrypt.init_app(app)

        login_manager.init_app(app)

        from home.oauth_apis import oauth
    oauth.init_app(app)



    from home import home_app
    app.register_blueprint(home_app)

    return app


def run_app():
    app = create_app()
    app.run()
