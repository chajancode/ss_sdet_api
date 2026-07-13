from types import SimpleNamespace

from models.posts.db_record_model import DBPostData
from models.posts.posts_model import (
                    PostCreatedOrPatchedResponse, Content, Title
)
from services.posts_service import PostsService


class FakePostsRepository:
    """
    Тестовый фейк репозитория постов.
    - fake: get_by_id отдаёт заранее заданную запись (без БД)
    - spy: запоминает, с какими id его звали
    """
    def __init__(self, record: DBPostData | None = None):
        self._record = record
        self.calls: list = []

    def get_by_id(self, post_id: int) -> DBPostData | None:
        """Запоминает id и возвращает заготовленную запись."""
        self.calls.append(post_id)
        return self._record


def _post_body(id=99, status="publish"):
    """
    Собирает тело ответа поста, чтобы не повторять в каждом тесте.
    """
    return PostCreatedOrPatchedResponse(
        id=id, status=status,
        title=Title(raw="t"), content=Content(raw="c"),
    )


class FakeClient:
    """
    Тестовый фейк апи-клиента.
    - fake: response отдаёт заранее заданный ответ от апи
    """
    def __init__(self, response):
        self._response = response

    def post(self, response_model, data=None, **kwargs):
        return self._response

    def delete(self, id=None, data=None, response_model=None, **kwargs):
        return self._response


def make_service(record: DBPostData | None = None):
    """
    Собирает сервис с фейковым репозиторием. Возвращает и сервис, и дублёр
    """
    repo = FakePostsRepository(record)
    service = PostsService(
        auth_data={"username": "u", "password": "p"},
        repository=repo,  # type: ignore
    )
    return service, repo


def test_get_db_record_returns_model():
    record = DBPostData(title="t", content="c", status="publish")
    service, repo = make_service(record)
    result = service._get_db_record(5)
    assert result is record
    assert repo.calls == [5]


def test_get_db_record_none_when_not_found():
    service, repo = make_service(record=None)
    result = service._get_db_record(123)
    assert result is None
    assert repo.calls == [123]


def test_get_db_record_none_id_skips_repository():
    service, repo = make_service()
    result = service._get_db_record(None)
    assert result is None
    assert repo.calls == []


def test_check_post_creation_build_response():
    api_body = PostCreatedOrPatchedResponse(
        id=99, status="publish",
        title=Title(raw="t"), content=Content(raw="c"),
    )
    api_response = SimpleNamespace(status_code=201, response_body=api_body)
    db_record = DBPostData(title='t', content='c', status='publish')

    service, repo = make_service(record=db_record)
    service.client = FakeClient(api_response)  # type: ignore

    result = service.check_post_creation(
        {'title': 't', 'content': 'c', 'status': 'publish'}
    )

    assert result.status_code == 201
    assert result.response_body is api_body
    assert result.db_record is db_record
    assert repo.calls == [99]


def test_check_post_deletion_checks_same_id_in_db():
    """
    check_post_deletion сверяет в БД ТОТ ЖЕ id, который удалял.
    """
    from models.posts.posts_model import PostDeletedResponse

    api_body = PostDeletedResponse(deleted=True, previous=_post_body(id=8))
    api_response = SimpleNamespace(status_code=200, response_body=api_body)

    service, repo = make_service(record=None)
    service.client = FakeClient(api_response)  # type: ignore

    result = service.check_post_deletion(id=8, test_data={"force": True})

    assert result.status_code == 200
    assert result.db_record is None
    assert repo.calls == [8]
