from typing import Optional, Type, TypeVar
from pydantic import BaseModel
import requests
from models.posts.api_responses_models import FullAPIResponse
from models.yandex.api_error_models import YandexApiError

T = TypeVar('T', bound=BaseModel)


class YandexFileUploader:

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
                response_body=parsed_body,  # type: ignore
                error=error
        )
