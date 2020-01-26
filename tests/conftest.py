import os
import tempfile
from unittest import mock

import pytest
from pytest_mock import mocker # noqa

import statsapp
from statsapp import db
from statsapp.models.user import User


@pytest.fixture(autouse=True)
def app(mocker): # noqa
    db_fd, db_path = tempfile.mkstemp()
    app = statsapp.create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
        'STRAVA_CLIENT_ID': '',
        'STRAVA_CLIENT_SECRET': '',
        'WITHINGS_CLIENT_ID': '',
        'WITHINGS_CLIENT_SECRET': '',
        'GOODREADS_CLIENT_ID': '',
        'GOODREADS_CLIENT_SECRET': '',
        'GOODREADS_USERID': '',
        'GSHEET_CLIENT_ID': '',
        'GSHEET_CLIENT_SECRET': '',
        'GSHEET_DOC_ID': '',
        'GOOGLEFIT_CLIENT_ID': '',
        'GOOGLEFIT_CLIENT_SECRET': '',
        'DEFAULT_USER_EMAIL': 'test.email@example.com',
    })

    with app.app_context():
        # let's mock out any more calls to create_app and have it just return the app we
        # have now. otherwise it will end up creating a non-test instance of the app :S
        # this doesn't prevent doing "from statsapp import create_app" from instantiating a non-test app though.        mocker.patch('statsapp.create_app', return_value=app)
        db.init_app(app)
        db.create_all()
        User.create_user(app.config['DEFAULT_USER_EMAIL'], 'password')

        print(id(app))
        yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_googlefit_api(mocker): # noqa
    m = mocker.patch('statsapp.apis.googlefit.GoogleFitAPI.get_stats_for_date')
    yield m

@pytest.fixture
def mock_withings_api(mocker): # noqa
    m = mocker.patch('statsapp.apis.withings.WithingsAPI.get_weight_data')
    yield m
