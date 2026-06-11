from typing import Generic, Optional, Type, TypeVar

from pydantic import BaseModel
from requests.auth import HTTPBasicAuth

from api.api_client import APIClient
from dao.base_dao import BaseDao
from models.posts.api_responses_models import FullAPIResponse


M = TypeVar('M', bound=BaseModel)
D = TypeVar('D', bound=BaseDao)


class BaseService(Generic[D]):
    """
    Базовый сервис для работы с API через HTTP-клиент.

    Предоставляет общие методы для создания, изменения и удаления ресурсов.
    Хранит DAO для доступа к данным.

    Args:
        auth_data (dict): Данные для HTTP Basic аутентификации.
        endpoint (str): Базовый URL API-эндпоинта.
        dao (D): Экземпляр DAO для работы с БД.
    """
    def __init__(
                self,
                endpoint: str,
                auth_data: Optional[dict[str, str]] = None,
                dao: Optional[D] = None,
                headers: Optional[dict[str, str]] = None
            ) -> None:
        """
        Инициализирует сервис.

        - Создаёт HTTPBasicAuth из переданных данных
        - Инициализирует APIClient
        - Сохраняет DAO

        Args:
            auth_data (dict): Словарь с полями 'username' и 'password'.
            endpoint(str): Базовый URL API.
            dao (BaseDao): Экземпляр DAO.
        """
        if auth_data is not None:
            self.auth = HTTPBasicAuth(**auth_data)
        else:
            self.auth = None
        self._last_created_id = None
        self.dao = dao
        self.headers = headers
        self.client = APIClient(endpoint, self.auth, headers=self.headers)

    def create(
            self, test_data: dict, response_model: Type[M]
            ) -> FullAPIResponse[M, BaseModel]:
        """
        Создаёт новую запись через POST-запрос.

        При успешном создании (статус 201) сохраняет ID созданной записи
        в атрибут `_last_created_id`.

        Args:
            test_data (dict): Данные для отправки в теле запроса.
            response_model (BaseModel): Pydantic-модель, \
            в которую будет десериализован ответ.

        Returns:
            FullAPIResponse[M]: Ответ от APIClient (объект с полями \
            status_code, response_body и др.).
        """
        response = self.client.post(test_data, response_model)

        if response.status_code == 201:
            self._last_created_id = response.response_body.id  # type: ignore
        return response

    def patch(
            self, id: int, test_data: dict, response_model: Type[M]
            ) -> FullAPIResponse[M, BaseModel]:
        """
        Обновляет запись через PATCH-запрос.

        Args:
            id (int): id обновляемого ресурса.
            test_data (dict): Данные для частичного обновления.
            response_model (BaseModel): Модель для десериализации ответа.

        Returns:
            FullAPIResponse[M]: Ответ от APIClient (объект с полями \
            status_code, response_body и др.).
        """
        return self.client.patch(
            id=id, data=test_data, response_model=response_model
        )

    def delete(
            self, id: int, test_data: dict, response_model: Type[M]
            ) -> FullAPIResponse[M, BaseModel]:
        """
        Удаляет запись через DELETE-запрос.

        Args:
            id (int): Идентификатор удаляемого ресурса.
            test_data (dict): Модификаторы запроса.
            response_model (BaseModel): Модель для десериализации ответа.

        Returns:
            FullAPIResponse[M]: Ответ от APIClient (объект с полями \
            status_code, response_body и др.).
        """
        return self.client.delete(
            id=id, data=test_data, response_model=response_model
        )

    def get_many(
            self,
            response_model: Type[M],
            params: Optional[dict] = None
    ) -> FullAPIResponse[list[M], BaseModel]:
        return self.client.get_many(response_model, params)

    def get_by_id(
            self,
            id: int,
            response_model: Type[M],
            params: Optional[dict] = None
    ) -> FullAPIResponse[M, BaseModel]:
        """
        Получает одну запись по ID через GET-запрос.

        Args:
            id (int): Идентификатор ресурса.
            response_model (BaseModel): Модель для десериализации ответа.
            params (Optional[dict]): Параметры запроса.

        Returns:
            FullAPIResponse[M]: Ответ с кодом статуса и телом ответа.
        """
        return self.client.get_by_id(id, response_model, params)
