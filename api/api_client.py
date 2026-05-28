from typing import Optional, Type, TypeVar

from pydantic import BaseModel
from requests import Session
from requests.auth import HTTPBasicAuth

from models.posts.api_responses_models import FullAPIResponse

M = TypeVar('M', bound=BaseModel)


class APIClient:
    """
    HTTP-клиент для взаимодействия с REST API.
    Выполняет запросы с BasicAuth, автоматической
     и десериализует ответы в Pydantic-модели.

    Attributes:
        session (Session): Сессия requests.
        endpoint (str): Базовый URL API.
        auth (HTTPBasicAuth): Данные для BasicAuth.
    """
    def __init__(self, endpoint: str, auth: HTTPBasicAuth) -> None:
        """
        Инициализирует API-клиент.

        Args:
            endpoint (str): Базовый URL эндпоинта
            auth (HTTPBasicAuth): Объект HTTPBasicAuth с именем пользователя \
            и паролем.
        """
        self.session = Session()
        self.endpoint: str = endpoint
        self.auth = auth

    def _request(
                self,
                method: str,
                response_model: Type[M],
                id: Optional[int] = None,
                data: Optional[dict] = None,
    ) -> FullAPIResponse[M]:
        """
        Выполняет HTTP-запрос и обрабатывает ответ.

        - Формирует URL
        - Отправляет запрос
        - Проверяет статус-код
        - Десериализует тело ответа

        Args:
            method (str): HTTP-метод
            response_model (BaseModel): Pydantic-модель для парсинга тела \
            ответа.
            id (int): Идентификатор для добавления в запрос.
            data: Данные для тела запроса.

        Returns:
            FullAPIResponse[M]: Объект, содержащий код статуса и \
            десериализованное тело.

        Raises:
            RuntimeError: Если статус-код ответа >= 400. В сообщение \
            включается код и текст ответа.
        """

        url = f'{self.endpoint}/{id}' if id else self.endpoint

        response = self.session.request(
            method=method,
            url=url,
            json=data,
            auth=self.auth,
        )
        if 200 <= response.status_code < 300:
            try:
                parsed_body = response_model(**response.json())
            except Exception as e:
                raise RuntimeError(f"Ошибка парсинга ответа: {e}") from e
        else:
            parsed_body = None

        return FullAPIResponse[M](
                status_code=response.status_code,
                response_body=parsed_body
        )

    def post(
                self,
                data: dict,
                response_model: Type[M]
    ) -> FullAPIResponse[M]:
        """
        Выполняет POST-запрос.

        Args:
            data (dict): Данные новой записи.
            response_model (BaseModel): Модель для десериализации тела ответа.

        Returns:
            FullAPIResponse[M]: Ответ с кодом статуса и телом запроса.
        """

        return self._request(
                method='POST',
                data=data,
                response_model=response_model

        )

    def patch(
                self,
                id: int,
                data: dict,
                response_model: Type[M]
    ) -> FullAPIResponse[M]:
        """
        Выполняет PATCH-запрос.

        Args:
            id (int): Идентификатор обновляемой записи.
            data (dict): Данные для обновления записи.
            response_model (BaseModel): Модель для десериализации тела ответа.

        Returns:
            FullAPIResponse[M]: Ответ с кодом статуса и тела запроса.
        """

        return self._request(
                method='PATCH',
                id=id,
                data=data,
                response_model=response_model,
        )

    def delete(
                self,
                id: int,
                data: dict,
                response_model: Type[M]
    ) -> FullAPIResponse[M]:
        """
        Выполняет DELETE-запрос.

        Args:
            id (int): Идентификатор удаляемого ресурса.
            data (dict): Модификаторы запроса.
            response_model (BaseModel): Модель для десериализации тела ответа.

        Returns:
            FullAPIResponse[M]: Ответ с кодом статуса и телом запроса.
        """
        return self._request(
                method='DELETE',
                id=id,
                data=data,
                response_model=response_model,
        )
