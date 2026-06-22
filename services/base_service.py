from typing import Optional, Type, TypeVar

from pydantic import BaseModel
from requests.auth import HTTPBasicAuth

from api.api_client import APIClient
from models.posts.api_responses_models import FullAPIResponse, WordPressError


M = TypeVar('M', bound=BaseModel)


class BaseService:
    """
    Базовый сервис для работы с API через HTTP-клиент.

    Предоставляет общие методы для создания, изменения и удаления ресурсов.

    Args:
        auth_data (dict): Данные для HTTP Basic аутентификации.
        endpoint (str): Базовый URL API-эндпоинта.
        headers (dict): Заголовки, добавляемые к запросам по умолчанию.
    """
    def __init__(
                self,
                endpoint: str,
                auth_data: Optional[dict[str, str]] = None,
                headers: Optional[dict[str, str]] = None
            ) -> None:
        """
        Инициализирует сервис.

        - Создаёт HTTPBasicAuth из переданных данных
        - Инициализирует APIClient с моделью ошибки WordPressError

        Args:
            auth_data (dict): Словарь с полями 'username' и 'password'.
            endpoint(str): Базовый URL API.
            headers (dict): Заголовки запросов по умолчанию.
        """
        if auth_data is not None:
            self.auth = HTTPBasicAuth(**auth_data)
        else:
            self.auth = None
        self._last_created_id = None
        self.headers = headers
        self.client = APIClient(
                        endpoint,
                        self.auth,
                        headers=self.headers,
                        error_model=WordPressError
        )

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
        response = self.client.post(response_model, data=test_data)

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
        """
        Получает список записей через GET-запрос.

        Args:
            response_model (BaseModel): Модель одного элемента списка.
            params (Optional[dict]): Параметры строки запроса.

        Returns:
            FullAPIResponse[list[M]]: Ответ со списком записей.
        """
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

    def get_one(
            self,
            response_model: Type[M],
            params: dict,
            error_model: Type[BaseModel]
    ) -> FullAPIResponse[M, BaseModel]:
        """
        Получает одну запись через GET-запрос по заданным параметрам.

        Args:
            response_model (BaseModel): Модель для десериализации ответа.
            params (dict): Параметры строки запроса.
            error_model (BaseModel): Модель для десериализации тела ошибки.

        Returns:
            FullAPIResponse[M]: Ответ с кодом статуса и телом/ошибкой.
        """
        return self.client.get_one(
            response_model, params=params, error_model=error_model
        )  # type: ignore
