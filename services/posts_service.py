from typing import Type, TypeVar

from pydantic import BaseModel

from api.endpoints import WordPressEndpoints as wpe
from dao.posts_dao import PostsDao
from models.posts.api_responses_models import FullAPIResponse
from models.posts.posts_model import (
                        PostCreatedOrPatchedResponse,
                        PostDeletedResponse
                    )
from models.posts.posts_service_response_model import (
                        PostsServiceDeleteResponse,
                        PostsServiceResponse
                    )
from services.base_service import BaseService
from utils.tuple_converter import tuple_to_post_model


M = TypeVar('M', bound=BaseModel)


class PostsService(BaseService[PostsDao]):
    """
    Сервис для работы с постами.

    - Предоставляет методы для создания, обновления и удаления постов
    с проверкой соответствия данных в БД.
    - Инкапсулирует логику вызовов API и чтения из DAO.

    Args:
        auth_data (dict): Данные для HTTP Basic аутентификации.
        dao (PostsDao): DAO для доступа к таблице постов. По умолчанию
            создаётся новый экземпляр PostsDao.
    """
    def __init__(self, auth_data: dict, dao: PostsDao) -> None:
        """
        Инициализирует сервис постов.

        Передаёт аутентификацию, эндпоинт и DAO в родительский класс
        BaseService.

        Args:
            auth_data (dict): Словарь с полями 'username' и 'password'.
            dao (CommentsDao): Экземпляр PostsDao. При создании без аргумента
                используется новый экземпляр.
        """
        super().__init__(wpe.POSTS_ENDPOINT, auth_data, dao)

    def _get_db_record(self, post_id: int | None):
        """
        Возвращает модель поста из БД по ID.

        Args:
            comment_id (int): Идентификатор поста или None.

        Returns:
            DBPostData | None
        """
        if post_id is None:
            return None
        record = self.dao.get_post_by_id(post_id)  # type: ignore
        if record is None:
            return None
        return tuple_to_post_model(record)

    def check_post_creation(self, test_data: dict):
        """
        Создаёт пост через API и проверяет результат в БД.

        - Вызывает родительский метод create
        - Сохраняет ID созданного поста
        - Получает соответствующую запись из БД
        - Возвращает объединённый ответ.

        Args:
            test_data (dict): Данные для создания поста.

        Returns:
            PostsServiceResponse: Объект, содержащий статус-код,
                тело ответа API и запись из БД (`BPostData`)
                для передачи в тесты.
        """
        response = self.create(test_data, PostCreatedOrPatchedResponse)
        return PostsServiceResponse(
            status_code=response.status_code,
            response_body=response.response_body,  # type: ignore
            db_record=self._get_db_record(self._last_created_id)
        )

    def check_post_patching(self, id: int, test_data: dict):
        """
        Обновляет последний созданный пост через API и сверяет с БД.

        Использует сохранённый `_last_created_id` для выполнения
        PATCH-запроса. После обновления получает обновлённую запись из БД
        и возвращает результат.

        Args:
            test_data (dict): Словарь с полями для обновления.

        Returns:
            PostsServiceResponse: Объект, содержащий статус-код,
                тело ответа API и запись из БД (`BPostData`)
                для передачи в тесты.
        """
        response = self.patch(
            id,  # type: ignore
            test_data,
            PostCreatedOrPatchedResponse
        )
        return PostsServiceResponse(
            status_code=response.status_code,
            response_body=response.response_body,  # type: ignore
            db_record=self._get_db_record(id)
        )

    def check_post_deletion(self, id: int, test_data: dict):
        """
        Удаляет последний созданный пост через API и проверяет
        отсутствие в БД.

        - Выполняет DELETE-запрос по сохранённому ID поста.
        - Ищет запись в БД по тому же ID (ожидается, что её уже нет).
        - Возвращает статус удаления и запись из БД.

        Args:
            test_data (dict): Модификаторы DELETE-запроса.

        Returns:
            PostsServiceDeleteResponse: Ответ API и результат запроса к БД.
        """

        response = self.delete(
            id=id,  # type: ignore
            test_data=test_data,
            response_model=PostDeletedResponse
        )
        db_record = self._get_db_record(
            self._last_created_id
            ) if self._last_created_id else None
        return PostsServiceDeleteResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=db_record  # type:ignore
        )

    def get_one_post(
            self,
            id: int,
            response_model: Type[M],
            params: dict | None = None
            ):
        return self.get_by_id(id, response_model, params)

    def get_many_posts(
            self,
            response_model: type[M],
            params: dict | None = None
            ) -> FullAPIResponse[list[M], BaseModel]:
        return self.get_many(response_model, params)
