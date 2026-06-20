from typing import Optional, Type, TypeVar
from pydantic import BaseModel
import requests
from models.posts.api_responses_models import FullAPIResponse
from models.yandex.api_error_models import YandexApiError
from models.yandex.success_api_response_models import SuccessApiResponse

T = TypeVar('T', bound=BaseModel)


class YandexFileManager:

    @staticmethod
    def upload_file(
        local_path: str,
        upload_url: str,
        response_model: Optional[Type[T]] = None,
        error_model: Type[BaseModel] = YandexApiError
    ) -> FullAPIResponse[T, BaseModel]:
        """
        Загружает файл на яндекс.диск по href

        Args:
            local_path (str): путь к локальному файлу
            upload_url (str): href для загрузки файла
        """
        parsed_body = None

        try:
            with open(local_path, 'rb') as file:
                response = requests.put(
                    url=upload_url,
                    data=file
                )
        except Exception as e:
            return FullAPIResponse(
                status_code=500,
                response_body=None,
                error=error_model(
                    error='Ошибка загркзки',
                    description=str(e),
                    message='Загрузка не удалась')
            )

        if 200 <= response.status_code < 300:
            try:
                if response.status_code == 204 or not response.text:
                    parsed_body = None
                if response_model:
                    parsed_body = response_model(**response.json())
                error = None
            except Exception as e:
                parsed_body = None
                raise RuntimeError(f"Ошибка парсинга ответа: {e}") from e
        else:
            parsed_body = None
            error = error_model(**response.json())

        return FullAPIResponse[T, BaseModel](
                status_code=response.status_code,
                response_body=parsed_body,
                error=error
        )

    @staticmethod
    def download_file(
        download_link: str,
        headers: dict | None,
        filename: str = 'data_downloaded.txt',
        response_model: Optional[Type[T]] = None,
        error_model: Type[BaseModel] = YandexApiError,
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        parsed_body = None
        error = None

        try:
            response = requests.get(url=download_link, headers=headers)
        except Exception as e:
            return FullAPIResponse(
                status_code=500,
                response_body=None,
                error=error_model(
                    error='Ошибка скачивантя',
                    description=str(e),
                    message='Запрос не удался',
                )
            )  # type: ignore

        if response.status_code in (200, 302):
            try:
                with open(filename, 'w') as file:
                    file.write(response.text)
            except Exception as e:
                return FullAPIResponse(
                    status_code=500,
                    response_body=None,
                    error=error_model(
                        error='Ошибка сохраненияч файла',
                        description=str(e),
                        message='Не удалось сохранить файл',
                    )
                )  # type: ignore

            try:
                if response.text and response_model:
                    parsed_body = response_model(**response.json())
            except Exception as e:
                raise RuntimeError(f"Ошибка парсинга ответа: {e}") from e

        else:
            parsed_body = None
            error = error_model(**response.json())

        return FullAPIResponse[T, BaseModel](
            status_code=response.status_code,
            response_body=parsed_body,
            error=error,
        )  # type: ignore

    @staticmethod
    def compare_files(
        local_filename: str,
        downloaded_filename: str
    ) -> tuple[bool, str]:
        with open(local_filename) as file:
            local_file = file.read()
        with open(downloaded_filename) as file:
            downloaded_file = file.read()
        match local_file == downloaded_file:
            case True:
                return True, 'Содержимое файлов одинаково'
            case _:
                return False, 'Cодержимое файлов отличается'
