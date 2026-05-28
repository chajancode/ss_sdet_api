import pytest

from dao.comments_dao import CommentsDao
from services.comments_service import CommentsService


@pytest.fixture(scope='session')
def comments_dao(database):
    return CommentsDao(database=database)


@pytest.fixture(scope='session')
def comments_service(auth_data, comments_dao):
    return CommentsService(auth_data, comments_dao)
