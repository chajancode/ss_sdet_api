from types import SimpleNamespace

from models.comments.db_record_model import DBCommentData
from services.comments_service import CommentsService
from models.comments.comments_model import (
    CommentCreatedOrPatchedResponse,
    CommentDeletedResponse,
    Content,
)


class FakeCommentsRepository:
    """
    Тестовый фейк репозитория камментов.
    - fake: get_by_id отдаёт заранее заданную запись (без БД)
    - spy: запоминает, с какими id его звали
    Ему достаточно иметь метод get_by_id - сервис использует только его
    """
    def __init__(self, record: DBCommentData | None = None):
        self._record = record
        self.calls: list = []

    def get_by_id(self, comment_id: int) -> DBCommentData | None:
        """
        Запоминает id и возвращает заготовленную запись.
        """
        self.calls.append(comment_id)
        return self._record


def _comment_body(id=2, post=14, status="approved"):
    """
    Тело ответа комментария.
    """
    return CommentCreatedOrPatchedResponse(
        id=id, post=post, status=status,
        content=Content(raw="c", rendered="c"),
    )


class FakeClient:
    """
    Фейк API-клиента: любой метод возвращает заготовленный ответ.
    """
    def __init__(self, response):
        self._response = response

    def post(self, response_model, data=None, **kwargs):
        return self._response

    def delete(self, id=None, data=None, response_model=None, **kwargs):
        return self._response


def make_service(record: DBCommentData | None = None):
    """
    Собирает сервис с фейковым репозиторием. Возвращает и сервис, и дублёр
    """
    repo = FakeCommentsRepository(record)
    service = CommentsService(
        auth_data={"username": "u", "password": "p"},
        repository=repo,  # type: ignore
    )
    return service, repo


def test_get_db_record_returns_model():
    record = DBCommentData(post=14, content="c")
    service, repo = make_service(record)

    result = service._get_db_record(2)

    assert result is record
    assert repo.calls == [2]


def test_get_db_record_none_when_not_found():
    service, repo = make_service(record=None)

    result = service._get_db_record(999)

    assert result is None
    assert repo.calls == [999]


def test_get_db_record_none_id_skips_repository():
    service, repo = make_service()

    result = service._get_db_record(None)

    assert result is None
    assert repo.calls == []


def test_check_comment_creation_build_response():
    """
    Собирает ответ из тела API + записи БД; id из ответа уходит в репозиторий.
    """
    api_body = _comment_body(id=2)
    api_response = SimpleNamespace(status_code=201, response_body=api_body)
    db_record = DBCommentData(post=14, content="c")

    service, repo = make_service(record=db_record)
    service.client = FakeClient(api_response)  # type: ignore

    result = service.check_comment_creation(
        {"post": 14, "content": "c", "status": "approved"}
    )

    assert result.status_code == 201
    assert result.response_body is api_body
    assert result.db_record is db_record
    assert repo.calls == [2]


def test_check_comment_deletion_checks_last_created_id():
    """
    Удаляет и сверяет в БД сохранённый _last_created_id.
    """
    api_body = CommentDeletedResponse(
        deleted=True, previous=_comment_body(id=2)
    )
    api_response = SimpleNamespace(status_code=200, response_body=api_body)

    service, repo = make_service(record=None)
    service.client = FakeClient(api_response)  # type: ignore
    service._last_created_id = 2

    result = service.check_comment_deletion({"force": True})

    assert result.status_code == 200
    assert result.db_record is None
    assert repo.calls == [2]
