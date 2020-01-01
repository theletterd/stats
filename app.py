from flask import Flask

import secret



def create_app():
    app = Flask(__name__)
    app.secret_key = secret.FLASK_SECRET_KEY

    # TODO move to a config somewhere
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./sqlite_database'

    from models import db
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from models import bcrypt
    bcrypt.init_app(app)

    from home import home_app
    app.register_blueprint(home_app)

    return app


def run_app():
    app = create_app()
    app.run()
