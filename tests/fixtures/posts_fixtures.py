import pytest

from dao.posts_dao import PostsDao
from services.posts_service import PostsService


@pytest.fixture(scope='session')
def posts_dao(database) -> PostsDao:
    return PostsDao(database=database)


@pytest.fixture(scope='session')
def posts_service(auth_data, posts_dao) -> PostsService:
    return PostsService(auth_data, posts_dao)
