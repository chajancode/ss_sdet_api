from typing import List, Optional, Type, TypeVar

from pydantic import BaseModel, TypeAdapter
from requests import Session
from requests.auth import HTTPBasicAuth

from models.posts.api_responses_models import FullAPIResponse, WordPressError

M = TypeVar('M', bound=BaseModel)
E = TypeVar('E', bound=BaseModel)


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
    def __init__(
            self,
            endpoint: str,
            auth: Optional[HTTPBasicAuth] = None,
            headers: Optional[dict[str, str]] = None
            ) -> None:
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
        self.headers = headers

    def _request(
                self,
                method: str,
                response_model: Type[M],
                id: Optional[int] = None,
                data: Optional[dict] = None,
                params: Optional[dict] = None,
                headers: Optional[dict] = None,
                error_model: Optional[Type[E]] = None,
    ) -> FullAPIResponse[M, E]:
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
        if error_model is None:
            error_model = WordPressError  # type: ignore

        url = f'{self.endpoint}/{id}' if id is not None else self.endpoint
        response = self.session.request(
            method=method,
            url=url,
            json=data,
            params=params,
            auth=self.auth,
            headers=headers
        )
        if 200 <= response.status_code < 300:
            try:
                if response.status_code == 204 or not response.text:
                    parsed_body = None
                else:
                    # print(f'APICLIENT response {response.json()}')

                    parsed_body = response_model(**response.json())
                error = None
            except Exception as e:
                raise RuntimeError(f"Ошибка парсинга ответа: {e}") from e
        else:
            parsed_body = None
            error = error_model(**response.json())  # type: ignore

        return FullAPIResponse[M, E](
                status_code=response.status_code,
                response_body=parsed_body,
                error=error  # type: ignore
        )

    def post(
                self,
                data: dict,
                response_model: Type[M]
    ) -> FullAPIResponse[M, BaseModel]:
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

    def put(
        self,
        response_model: Type[M],
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        error_model: Optional[Type[E]] = None
    ) -> FullAPIResponse[M, BaseModel]:
        """
        Выполняет PUT-запрос.

        Args:
            data (dict): Данные новой записи.
            response_model (BaseModel): Модель для десериализации тела ответа.


        Returns:
            FullAPIResponse[M]: Ответ с кодом статуса и телом запроса.
        """

        return self._request(
                method='PUT',
                response_model=response_model,
                params=params,
                headers=headers,
                error_model=error_model  # type: ignore
        )

    def patch(
                self,
                id: int,
                data: dict,
                response_model: Type[M]
    ) -> FullAPIResponse[M, BaseModel]:
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
                response_model: Type[M],
                data: Optional[dict] = None,
                id: Optional[int] = None,
                params: Optional[dict] = None,
                headers: Optional[dict] = None,
                error_model: Optional[Type[E]] = None
    ) -> FullAPIResponse[M, BaseModel]:
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
                params=params,
                headers=headers,
                response_model=response_model,
                error_model=error_model  # type: ignore
        )

    def get_by_id(
        self,
        id: int,
        response_model: Type[M],
        params: Optional[dict] = None,
    ) -> FullAPIResponse[M, BaseModel]:
        """
        Выполняет GET-запрос для получения одного объеута по ID.

        Args:
            id (int): Идентификатор записи.
            response_model (BaseModel): Pydantic-модель для тела ответа.
            params: Дополнительные параметры.

        Returns:
            FullAPIResponse[M]: Ответ с кодом статуса и десериализованным \
                телом.
        """
        return self._request(
            method='GET',
            id=id,
            params=params,
            response_model=response_model,
        )

    def get_one(
        self,
        response_model: Type[M],
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        error_model: Optional[Type[E]] = None
    ) -> FullAPIResponse[M, BaseModel]:
        return self._request(
            method='GET',
            response_model=response_model,
            params=params,
            headers=headers,
            error_model=error_model  # type: ignore
        )

    def get_many(
        self,
        response_model: Type[M],
        params: Optional[dict] = None
    ) -> FullAPIResponse[List[M], BaseModel]:
        response = self.session.request(
            method='GET',
            url=self.endpoint,
            params=params,
            auth=self.auth,
            headers={'Accept': 'application/json'}
        )
        if 200 <= response.status_code < 300:
            parsed_body = TypeAdapter(
                List[response_model]).validate_python(response.json())
            error = None
        else:
            parsed_body = []
            error = WordPressError(
                **response.json()) if response.text else None
        return FullAPIResponse(
            status_code=response.status_code,
            response_body=parsed_body,
            error=error
        )
