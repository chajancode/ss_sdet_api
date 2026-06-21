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
        dao (PostsDao): DAO для доступа к таблице постов.
    """
    def __init__(self, auth_data: dict, dao: PostsDao) -> None:
        """
        Инициализирует сервис постов.

        Передаёт аутентификацию, эндпоинт и DAO в родительский класс
        BaseService.

        Args:
            auth_data (dict): Словарь с полями 'username' и 'password'.
            dao (PostsDao): Экземпляр PostsDao.
        """
        super().__init__(wpe.POSTS_ENDPOINT, auth_data, dao)

    def _get_db_record(self, post_id: int | None):
        """
        Возвращает модель поста из БД по ID.

        Args:
            post_id (int | None): Идентификатор поста или None.

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
        Обновляет пост через API по переданному id и сверяет с БД.

        Выполняет PATCH-запрос для указанного поста, затем получает
        обновлённую запись из БД и возвращает результат.

        Args:
            id (int): Идентификатор обновляемого поста.
            test_data (dict): Словарь с полями для обновления.

        Returns:
            PostsServiceResponse: Объект со статус-кодом, телом ответа API
                и записью из БД (DBPostData) для передачи в тесты.
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
        Удаляет пост через API по переданному id и проверяет отсутствие в БД.

        - Выполняет DELETE-запрос по указанному id поста.
        - Ищет запись в БД (ожидается, что её уже нет).
        - Возвращает статус удаления и запись из БД.

        Args:
            id (int): Идентификатор удаляемого поста.
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
        """
        Получает один пост по id через GET-запрос.

        Args:
            id (int): Идентификатор поста.
            response_model (Type[M]): Модель для десериализации ответа.
            params (dict | None): Параметры строки запроса.

        Returns:
            FullAPIResponse[M]: Ответ со статус-кодом и телом поста.
        """
        return self.get_by_id(id, response_model, params)

    def get_many_posts(
            self,
            response_model: type[M],
            params: dict | None = None
            ) -> FullAPIResponse[list[M], BaseModel]:
        return self.get_many(response_model, params)
