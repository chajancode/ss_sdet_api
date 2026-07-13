import logging
from typing import IO, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel, TypeAdapter
from requests import Response, Session
from requests.auth import HTTPBasicAuth

from models.posts.api_responses_models import FullAPIResponse

logger = logging.getLogger(__name__)

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
            headers: Optional[dict[str, str]] = None,
            error_model: Optional[Type[BaseModel]] = None
            ) -> None:
        """
        Инициализирует API-клиент.

        Args:
            endpoint (str): Базовый URL эндпоинта.
            auth (HTTPBasicAuth): Объект HTTPBasicAuth с именем пользователя \
            и паролем.
            headers (dict): Заголовки, добавляемые к запросам по умолчанию.
            error_model (Type[BaseModel]): Модель по умолчанию для разбора \
            тела ошибочного ответа. Используется, когда конкретный вызов не \
            передал свой error_model. Если не задана, тело ошибки не \
            десериализуется (error остаётся None).
        """
        self.session = Session()
        self.endpoint: str = endpoint
        self.auth = auth
        self.headers = headers
        self.error_model = error_model
        logger.debug(
            f'APIClient создан: endpoint={endpoint}, '
            f'auth={"True" if auth else "False"}, error_model={error_model}'
        )

    @staticmethod
    def _parse_error(
        response: Response,
        error_model: Optional[Type[E]]
    ) -> Optional[E]:
        """
        Преобразует тело ошибочного ответа в error_model.
        Args:
            response (Response): Ответ requests с кодом >= 400.
            error_model (Type[BaseModel] | None): Модель для тела \
            ошибки.

        Returns:
            Optional[E]: Экземпляр error_model, либо None если модель не \
            задана или тело ответа пустое.

        Raises:
            RuntimeError: Если тело есть, но не преобразуется в модель. \
            В сообщение включаются статус-код и сырое тело ответа.
        """
        if error_model is None or not response.text:
            return None
        try:
            return error_model(**response.json())
        except Exception as e:
            raise RuntimeError(
                f'Ошибка парсинга тела ошибки '
                f'(статус {response.status_code}): {response.text!r}'
            ) from e

    def _request(
                self,
                method: str,
                response_model: Type[M],
                id: Optional[int] = None,
                url: Optional[str] = None,
                data: Union[dict, IO[bytes], None] = None,
                json: Optional[dict] = None,
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
            error_model (Type[BaseModel]): Модель тела ошибки. Если не \
            передана, берктся error_model клиента.

        Returns:
            FullAPIResponse[M]: Объект, содержащий код статуса и \
            десериализованное тело.

        Raises:
            RuntimeError: Если тело ответа не удалось десериализовать \
            как успешное (в response_model), так и ошибочное (в error_model).
        """
        if error_model is None:
            error_model = self.error_model  # type: ignore

        if url is None:
            url = f'{self.endpoint}/{id}' if id is not None else self.endpoint

        logger.info(f'-> {method} {url}')
        if params:
            logger.debug(f'params: {params}')

        response = self.session.request(
            method=method,
            url=url,
            json=json,
            params=params,
            auth=self.auth,
            headers=headers,
            data=data
        )
        if 200 <= response.status_code < 300:
            logger.info(f'<- {response.status_code} {method} {url}')
            try:
                if response.status_code == 204 or not response.text:
                    parsed_body = None
                else:
                    parsed_body = response_model(**response.json())
                error = None
            except Exception as e:
                logger.error(f'Ошибка парсинга ответа {url}: {e}')
                raise RuntimeError(f'Ошибка парсинга ответа: {e}') from e
        else:
            logger.warning(
                f'<- {response.status_code} {method} \
                    {url}: {response.text[:200]}'
            )
            parsed_body = None
            error = self._parse_error(response, error_model)  # type: ignore

        return FullAPIResponse[M, E](
                status_code=response.status_code,
                response_body=parsed_body,
                error=error  # type: ignore
        )

    def post(
                self,
                response_model: Type[M],
                url: Optional[str] = None,
                data: Optional[dict] = None,
                params: Optional[dict] = None,
                error_model: Optional[Type[E]] = None,
    ) -> FullAPIResponse[M, BaseModel]:
        """
        Выполняет POST-запрос.

        Args:
            response_model (BaseModel): Модель для десериализации тела ответа.
            url (str): Полный URL запроса. Если не задан, используется \
            endpoint клиента.
            data (dict): Данные тела запроса.
            params (dict): Параметры строки запроса.
            error_model (Type[BaseModel]): Модель тела ошибки. Если не \
            передана, берётся error_model клиента.

        Returns:
            FullAPIResponse[M]: Ответ с кодом статуса и телом/ошибкой.
        """

        return self._request(
                method='POST',
                url=url,
                params=params,
                data=data,
                response_model=response_model,
                error_model=error_model,
                headers=self.headers
        )

    def put(
        self,
        response_model: Type[M],
        url: Optional[str] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        error_model: Optional[Type[E]] = None,
        data: Union[dict, IO[bytes], None] = None
    ) -> FullAPIResponse[M, BaseModel]:
        """
        Выполняет PUT-запрос.

        Args:
            response_model (BaseModel): Модель для десериализации тела ответа.
            url (str): Полный URL запроса. Если не задан, используется \
            endpoint клиента.
            params (dict): Параметры строки запроса.
            headers (dict): Заголовки запроса.
            error_model (Type[BaseModel]): Модель тела ошибки. Если не \
            передана, берётся error_model клиента.
            data (dict | IO[bytes]): Данные тела запроса.

        Returns:
            FullAPIResponse[M]: Ответ с кодом статуса и телом/ошибкой.
        """

        return self._request(
                method='PUT',
                url=url,
                data=data,
                response_model=response_model,
                params=params,
                headers=headers,
                error_model=error_model  # type: ignore
        )

    def patch(
                self,
                id: int,
                data: dict,
                response_model: Type[M],
                params: Optional[dict] = None,
                headers: Optional[dict] = None,
                error_model: Optional[Type[E]] = None
    ) -> FullAPIResponse[M, BaseModel]:
        """
        Выполняет PATCH-запрос.

        Args:
            id (int): Идентификатор обновляемой записи (подставляется в URL).
            data (dict): Данные для обновления записи.
            response_model (BaseModel): Модель для десериализации тела ответа.
            params (dict): Параметры строки запроса.
            headers (dict): Заголовки запроса.
            error_model (Type[BaseModel]): Модель тела ошибки. Если не \
            передана, берётся error_model клиента.

        Returns:
            FullAPIResponse[M]: Ответ с кодом статуса и телом/ошибкой.
        """

        return self._request(
                method='PATCH',
                id=id,
                data=data,
                params=params,
                headers=headers,
                response_model=response_model,
                error_model=error_model  # type: ignore
        )

    def delete(
                self,
                response_model: Type[M],
                url: Optional[str] = None,
                data: Optional[dict] = None,
                id: Optional[int] = None,
                params: Optional[dict] = None,
                headers: Optional[dict] = None,
                error_model: Optional[Type[E]] = None
    ) -> FullAPIResponse[M, BaseModel]:
        """
        Выполняет DELETE-запрос.

        Args:
            response_model (BaseModel): Модель для десериализации тела ответа.
            url (str): Полный URL запроса. Если не задан, используется \
            endpoint клиента (с подстановкой id, если передан).
            data (dict): Модификаторы запроса в теле.
            id (int): Идентификатор удаляемого ресурса (подставляется в URL).
            params (dict): Параметры строки запроса.
            headers (dict): Заголовки запроса.
            error_model (Type[BaseModel]): Модель тела ошибки. Если не \
            передана, берётся error_model клиента.

        Returns:
            FullAPIResponse[M]: Ответ с кодом статуса и телом/ошибкой.
        """
        return self._request(
                method='DELETE',
                url=url,
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
        url: Optional[str] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        error_model: Optional[Type[E]] = None
    ) -> FullAPIResponse[M, BaseModel]:
        """
        Выполняет GET-запрос по URL.

        Args:
            response_model (BaseModel): Модель для десериализации тела ответа.
            url (str): Полный URL запроса. Если не задан, используется \
            endpoint клиента.
            params (dict): Параметры строки запроса.
            headers (dict): Заголовки запроса.
            error_model (Type[BaseModel]): Модель тела ошибки.

        Returns:
            FullAPIResponse[M]: Ответ с кодом статуса и телом/ошибкой.
        """
        return self._request(
            method='GET',
            url=url,
            response_model=response_model,
            params=params,
            headers=headers,
            error_model=error_model  # type: ignore
        )

    def get_many(
        self,
        response_model: Type[M],
        params: Optional[dict] = None,
        error_model: Optional[Type[E]] = None
    ) -> FullAPIResponse[List[M], BaseModel]:
        """
        Выполняет GET-запрос, ожидающий в ответе список объектов.

        Args:
            response_model (BaseModel): Модель одного элемента списка. Тело \
            преобразуетмся как List[response_model].
            params (dict): Параметры строки запроса.
            error_model (Type[BaseModel]): Модель тела ошибки. Если не \
            передана, берётся error_model клиента.

        Returns:
            FullAPIResponse[list[M]]: Ответ со списком объектов и телом \
            ошибки.
        """
        if error_model is None:
            error_model = self.error_model  # type: ignore

        logger.info(f'-> GET (many) {self.endpoint}')

        response = self.session.request(
            method='GET',
            url=self.endpoint,
            params=params,
            auth=self.auth,
            headers=self.headers
        )
        if 200 <= response.status_code < 300:
            logger.info(
                f'<- {response.status_code} GET (many) {self.endpoint}'
            )
            parsed_body = TypeAdapter(
                List[response_model]).validate_python(response.json())
            error = None
        else:
            logger.warning(
                f'<- {response.status_code} GET {self.endpoint} (many): '
                f'{response.text[:200]}'
            )
            parsed_body = []
            error = self._parse_error(response, error_model)
        return FullAPIResponse(
            status_code=response.status_code,
            response_body=parsed_body,
            error=error
        )
