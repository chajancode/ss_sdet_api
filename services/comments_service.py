from api.endpoints import WordPressEndpoints as wpe
from dao.comments_dao import CommentsDao
from models.comments.comment_service_response_model import (
                        CommentsServiceDeleteResponse,
                        CommentsServiceResponse
                    )
from models.comments.comments_model import (
                        CommentCreatedOrPatchedResponse,
                        CommentDeletedResponse
                    )
from services.base_service import BaseService
from utils.tuple_converter import tuple_to_comm_model


class CommentsService(BaseService[CommentsDao]):
    """
    Сервис для работы с комментариями.

    - Предоставляет методы для создания, обновления и удаления комментариев
    с проверкой соответствия данных в БД.
    - Инкапсулирует логику вызовов API
    и чтения из DAO.

    Args:
        auth_data (dict): Данные для HTTP Basic аутентификации \
        (username/password).
        dao (CommentsDao): DAO для доступа к таблице комментариев. По \
        умолчанию создаётся новый экземпляр CommentsDao.
    """
    def __init__(
            self, auth_data: dict, dao: CommentsDao = CommentsDao()
            ) -> None:
        """
        Инициализирует сервис комментариев.

        Передаёт аутентификацию, эндпоинт \
        и DAO в родительский класс BaseService.

        Args:
            auth_data (dict): Словарь с полями 'username' и 'password'.
            dao (CommentsDao): Экземпляр CommentsDao.
        """
        super().__init__(auth_data, wpe.COMMENTS_ENDPOINT, dao)

    def _get_db_record(self, comment_id: int | None):
        """
        Возвращает данные комментария из БД по id.

        Args:
            comment_id (int | None): Идентификатор комментария или None.

        Returns:
            DBCommentData | None.
        """
        if comment_id is None:
            return None
        return tuple_to_comm_model(
            *self.dao.get_comment_by_id(comment_id)
        )

    def check_comment_creation(self, test_data: dict):
        """
        Создаёт комментарий через API и проверяет результат в БД.

        - Вызывает родительский метод create
        - Сохраняет ID созданного комментария для последующих проверок
        - Получает соответствующую запись из БД
        - Возвращает объединённый ответ.

        Args:
            test_data (dict): Данные для создания комментария
        Returns:
            CommentsServiceResponse: Объект, содержащий статус-код, \
            тело ответа API
            и запись из БД (DBCommentData) для передачи в тесты.
        """
        response = self.create(test_data, CommentCreatedOrPatchedResponse)

        return CommentsServiceResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=self._get_db_record(self._last_created_id)
        )

    def check_comment_patching(self, test_data: dict):
        """
        Обновляет последний созданный комментарий через API и сверяет с БД.

        Использует сохранённый `_last_created_id` для выполнения PATCH-запроса.
        После обновления получает обновлённую запись из БД и возвращает \
        результат.

        Args:
            test_data (dict): Словарь с полями для обновления.

        Returns:
            CommentsServiceResponse: Объект, содержащий статус-код, \
            тело ответа API
            и запись из БД (DBCommentData) для передачи в тесты.
        """
        response = self.patch(
            self._last_created_id,  # type: ignore
            test_data,
            CommentCreatedOrPatchedResponse
        )

        return CommentsServiceResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=self._get_db_record(self._last_created_id)
        )

    def check_comment_deletion(self, test_data: dict):
        """
        Удаляет последний созданный комментарий через API \
        и проверяет отсутствие в БД.

        - Выполняет DELETE-запрос по сохранённому ID комментария
        - Ищет запись в БД по тому же ID (ожидается, что её уже нет)
        - Возвращает статус удаления и запись из БД

        Args:
            test_data (dict): Модификаторы DELETE-запроса

        Returns:
            CommentsServiceDeleteResponse: Ответ API и результат запроса к БД
        """
        response = self.delete(
            self._last_created_id,  # type: ignore
            test_data,
            CommentDeletedResponse
        )

        db_record = self.dao.get_comment_by_id(
            self._last_created_id
            ) if self._last_created_id else None
        return CommentsServiceDeleteResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=db_record  # type:ignore
        )
