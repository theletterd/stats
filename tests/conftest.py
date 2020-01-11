import os
import tempfile

import pytest

from statsapp import db
from statsapp.models.user import User
from statsapp import create_app


@pytest.fixture(scope='session', autouse=True)
def app():
    db_fd, db_path = tempfile.mkstemp()
    print(db_path)
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
        'STRAVA_CLIENT_ID': '',
        'STRAVA_CLIENT_SECRET': '',
        'GOODREADS_CLIENT_ID': '',
        'GOODREADS_CLIENT_SECRET': '',
        'GOODREADS_USERID': '',
        'GSHEET_CLIENT_ID': '',
        'GSHEET_CLIENT_SECRET': '',
        'GOOGLEFIT_CLIENT_ID': '',
        'GOOGLEFIT_CLIENT_SECRET': '',
        'DEFAULT_USER_EMAIL': 'test.email@example.com',
    })

    with app.app_context():
        db.init_app(app)
        db.create_all()
        User.create_user(app.config['DEFAULT_USER_EMAIL'], 'password')

        yield app


    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()
