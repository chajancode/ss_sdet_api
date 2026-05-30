import pytest

from config.credentials import API_USERNAME, API_PASSWORD
from database import Database
from config.db_config import db_settings
from database_session import DatabaseSession

pytest_plugins = [
    'tests.fixtures.posts_fixtures',
    'tests.fixtures.comments_fixtures'
]


@pytest.fixture(scope='session')
def auth_data():
    return {'username': API_USERNAME, 'password': API_PASSWORD}


@pytest.fixture(scope='session')
def database():
    return Database(db_settings=db_settings)


@pytest.fixture(scope='session')
def session():
    with DatabaseSession(db_settings=db_settings) as sess:
        yield sess
