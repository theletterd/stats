import os
import tempfile
from unittest import mock

import pytest
from pytest_mock import mocker # noqa

import statsapp
from statsapp import config
from statsapp.datastore_config import CACHE_CONFIG
from statsapp.datastore_config import DB_CONFIG
from statsapp import db
from statsapp.models.user import User


@pytest.fixture(autouse=True, scope='session') # ideally make this scoped to session
def testing_database(session_mocker):
    db_fd, db_path = tempfile.mkstemp()
    print(db_path)
    db_uri = 'sqlite:///' + db_path
    test_db_config = {
        'SQLALCHEMY_DATABASE_URI': db_uri
    }
    session_mocker.patch.dict(DB_CONFIG, {'SQLALCHEMY_DATABASE_URI': db_uri})

    yield # tests happen

    # teardown
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(autouse=True, scope='session')
def no_cache(session_mocker):
    session_mocker.patch.dict(CACHE_CONFIG, {'CACHE_TYPE': 'NullCache'})


@pytest.fixture(autouse=True)
def app(): # noqa

    app = statsapp.create_app({
        'TESTING': True,
        'DEFAULT_USER_EMAIL': 'test.email@example.com',
    })

    with app.app_context():
        db.create_all()
        User.create_user(app.config['DEFAULT_USER_EMAIL'], 'password')

        yield app

        # teardown
        db.drop_all()


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
