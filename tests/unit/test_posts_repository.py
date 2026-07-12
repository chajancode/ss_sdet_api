import pytest

from database.repositories.posts_repository import PostsRepository
from models.posts.db_record_model import DBPostData
from models.posts.post_create_and_response_dbc import ExpectedPostModel
from utils.string_utils import to_slug


class FakePostsDao:
    """
    Фейк DAO постов: заготовленные ответы + запись вызовов (fake + spy).
    """
    def __init__(self, row=None, insert_id: int = 1):
        self._row = row
        self._insert_id = insert_id
        self.selected: list = []
        self.inserted: list = []
        self.deleted: list = []

    def select_by_id(self, post_id):
        self.selected.append(post_id)
        return self._row

    def insert(self, params):
        self.inserted.append(params)
        return self._insert_id

    def delete(self, post_id):
        self.deleted.append(post_id)


def test_row_to_model_maps_fields():
    """
    Маппинг: кортеж БД -> доменная модель.
    """
    model = PostsRepository._row_to_model(("title", "content", "publish"))
    assert model == DBPostData(
        title="title", content="content", status="publish"
    )


def test_get_by_id_maps_row():
    """
    Запись найдена: строка от DAO превращается в модель, \
        DAO вызван с тем же id.
    """
    dao = FakePostsDao(row=("t", "c", "publish"))
    repo = PostsRepository(dao)  # type: ignore

    result = repo.get_by_id(5)

    assert result == DBPostData(title="t", content="c", status="publish")
    assert dao.selected == [5]


def test_get_by_id_none_when_not_found():
    """
    Не найдено: DAO вернул None -> репозиторий тоже None.
    """
    dao = FakePostsDao(row=None)
    repo = PostsRepository(dao)  # type: ignore

    assert repo.get_by_id(123) is None
    assert dao.selected == [123]


def test_create_builds_params_and_returns_id():
    """
    Запись добавлена: create собирает верный кортеж \
        параметров и возвращает id от DAO.
    """
    dao = FakePostsDao(insert_id=42)
    repo = PostsRepository(dao)  # type: ignore
    post = ExpectedPostModel(
        title="Мой пост", content="текст", status="publish"
    )

    new_id = repo.create(post)

    assert new_id == 42
    assert dao.inserted == [
        (1, "текст", "Мой пост", "publish", to_slug("Мой пост"), "post")
    ]


def test_create_raises_when_no_id():
    """
    Если БД вернула не int - create бросает ValueError.
    """
    dao = FakePostsDao(insert_id="not-an-int")  # type: ignore
    repo = PostsRepository(dao)  # type: ignore
    post = ExpectedPostModel(title="t", content="c", status="publish")

    with pytest.raises(ValueError):
        repo.create(post)
