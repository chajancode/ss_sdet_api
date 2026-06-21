from typing import Optional

from api.api_client import APIClient
from api.endpoints import YandexEndpoints as ye
from models.posts.api_responses_models import FullAPIResponse
from models.yandex.api_error_models import YandexApiError
from models.yandex.success_api_response_models import (
                                    SuccessApiResponse,
                                    SuccessGetUploadUrl
                                )
from models.yandex.resource_models import (
                                    FileModel,
                                    FilesListModel,
                                    FolderModel,
                                    TrashModel
                                )
from models.yandex.get_user_data_model import GetUserDataResponse
from utils.data_extraction import extract_deleted_folder_path_from_trash
from utils.data_generators import GenerateRandomTexts
from utils.yandex_file_manager import YandexFileManager


class YandexService:
    """
    Сервис для работы с Яндекс-Диском через REST API.

    Оборачивает APIClient и предоставляет методы для операций с папками,
    файлами и корзиной: создание/удаление/восстановление папок, загрузка,
    копирование и скачивание файлов, получение списков записей.

    Attributes:
        headers (dict): Заголовки с OAuth-токеном для авторизации.
        client (APIClient): HTTP-клиент с моделью ошибки YandexApiError.
    """
    def __init__(
            self,
            headers: dict[str, str] | None = None
    ) -> None:
        """
        Инициализирует сервис Яндекс-Диска.

        Args:
            headers (dict | None): Заголовки авторизации (OAuth-токен).
                Если не заданы, запросы уйдут без авторизации.
        """
        self.headers = headers
        self.client = APIClient(
            endpoint=ye.DISK_ENDPOINT,
            headers=headers,
            error_model=YandexApiError
        )

    def get_authorized_user(self):
        """
        Возвращает данные авторизованного пользователя Яндекс-Диска.

        Запрос уходит с заголовками авторизации.

        Returns:
            FullAPIResponse[GetUserDataResponse, YandexApiError]: Данные \
            пользователя при успехе.
        """
        return self.client.get_one(
            response_model=GetUserDataResponse,
            headers=self.headers
        )

    def get_unauthorized_user(
            self
    ) -> FullAPIResponse[GetUserDataResponse, YandexApiError]:
        """
        Негативный сценарий получения данных неавторизованного пользователя.

        Returns:
            FullAPIResponse[GetUserDataResponse, YandexApiError]: Ответ с \
            кодом 401 и телом ошибки.
        """
        return self.client.get_one(
            response_model=GetUserDataResponse
        )  # type: ignore

    def create_folder(
            self,
            params: Optional[dict] = None
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        """
        Создаёт папку на Яндекс-Диске.

        Args:
            params (dict): Параметры запроса, обязателен 'path'.

        Returns:
            FullAPIResponse[SuccessApiResponse, YandexApiError]: Результат \
            создания.
        """
        return self.client.put(
            response_model=SuccessApiResponse,
            headers=self.headers,
            params=params,
            url=ye.DISK_RESOURCES
        )  # type: ignore

    def delete_folder(
            self,
            permanently: bool = False,
            params: Optional[dict] = None
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        """
        Удаляет папку.

        Args:
            permanently (bool): True - удалить безвозвратно, False — в корзину.
            params (dict): Параметры запроса, обязателен 'path'.

        Returns:
            FullAPIResponse[SuccessApiResponse, YandexApiError]: Результат \
            удаления.
        """
        parameters = {'permanently': permanently}
        if params is not None:
            parameters.update(params)
        return self.client.delete(
            response_model=SuccessApiResponse,
            headers=self.headers,
            params=parameters,
            url=ye.DISK_RESOURCES
        )  # type: ignore

    def folder_in_storage(
            self,
            params: dict
    ) -> FullAPIResponse[FolderModel, YandexApiError]:
        """
        Возвращает метаданные ресурса по его пути.

        Args:
            params (dict): Параметры запроса, обязателен 'path'.

        Returns:
            FullAPIResponse[FolderModel, YandexApiError]: Метаданные папки \
            или тело ошибки, если папки нет.
        """
        return self.client.get_one(
            params=params,
            headers=self.headers,
            response_model=FolderModel,
            url=ye.DISK_RESOURCES
            )  # type: ignore

    def is_folder_in_trash(
            self,
            params: dict
    ) -> str | bool:
        """
        Ищет папку в корзине по имени.

        Args:
            params (dict): Параметры с ключом 'path' - имя искомой папки.

        Returns:
            str | bool: Путь папки внутри корзины, если найдена, иначе False.
        """
        items_in_trash = self.client.get_one(
            response_model=TrashModel,
            headers=self.headers,
            url=ye.DISK_TRASH
        )
        if items_in_trash.response_body:
            folder_path = extract_deleted_folder_path_from_trash(
                items_in_trash.response_body, params['path']
            )
            return folder_path
        return False

    def check_folder_exists(self, params: dict) -> bool:
        """
        Проверяет, существует ли папка с указанным путем.

        Args:
            params (dict): Параметры с ключом 'path'.

        Returns:
            bool: True, если папка найдена и её имя совпадает с 'path'.
        """
        folder = self.folder_in_storage(params)
        if folder.response_body and \
                folder.response_body.name == params['path']:
            return True
        return False

    def get_folder_name_doesnt_exist(self) -> dict[str, str]:
        """
        Подбирает случайное имя папки, которой ещё нет на Яндекс-Диске.

        Returns:
            dict[str, str]: Словарь {'path': <свободное имя>}.
        """
        while True:
            params = {'path': GenerateRandomTexts.generate_word()}
            if not self.check_folder_exists(params):
                return params

    def _restore(
            self, params: dict
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        """
        Восстанавливает ресурс из корзины.

        Args:
            params (dict): Параметры с ключом 'path' - путь в корзине.

        Returns:
            FullAPIResponse[SuccessApiResponse, YandexApiError]: Результат \
            восстановления.
        """
        return self.client.put(
            response_model=SuccessApiResponse,
            headers=self.headers,
            params=params,
            url=ye.DISK_TRASH_RESTORE
        )  # type: ignore

    def restore_deleted_folder(
            self,
            params: dict
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        """
        Находит удалённую папку в корзине и восстанавливает её.

        Args:
            params (dict): Параметры с ключом 'path' — имя папки.

        Returns:
            FullAPIResponse[SuccessApiResponse, YandexApiError]: Результат \
            восстановления.
        """
        folder_name = self.is_folder_in_trash(params=params)
        return self._restore({'path': folder_name})

    def restore_folder_doesnt_exist(
            self,
            params: dict
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        """
        Пытается восстановить несуществующую папку (негативный сценарий).

        Args:
            params (dict): Параметры с ключом 'path'.

        Returns:
            FullAPIResponse[SuccessApiResponse, YandexApiError]: Тело ошибки.
        """
        return self._restore(params=params)

    def empty_trash(self):
        """
        Очищает корзину Яндекс-Диска (DELETE /trash/resources).
        """
        self.client.delete(
            response_model=SuccessApiResponse,
            headers=self.headers,
            url=ye.DISK_TRASH
        )

    def request_upload_link(
            self,
            params: dict
    ) -> FullAPIResponse[SuccessGetUploadUrl, YandexApiError]:
        """
        Запрашивает ссылку для загрузки файла.

        Args:
            params (dict): Параметры с ключом 'path' — путь к файлу на Диске

        Returns:
            FullAPIResponse[SuccessGetUploadUrl, YandexApiError]: Ответ с \
            полем href для загрузки.
        """
        return self.client.get_one(
            response_model=SuccessGetUploadUrl,
            params=params,
            headers=self.headers,
            url=ye.DISK_UPLOAD
        )  # type: ignore

    def upload_file(
            self,
            path_to_local_file: str,
            upload_url: str
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        """
        Загружает локальный файл по полученному href.

        Args:
            path_to_local_file (str): Путь к локальному файлу.
            upload_url (str): href из request_upload_link.

        Returns:
            FullAPIResponse[SuccessApiResponse, YandexApiError]: Результат \
            загрузки.
        """
        response = YandexFileManager.upload_file(
            path_to_local_file,
            upload_url
        )
        return response  # type: ignore

    def copy_file(
            self,
            copy_from: str,
            copy_to: str
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        """
        Копирует файл внутри Яндекс-Диска.

        Args:
            copy_from (str): Путь-источник.
            copy_to (str): Путь-назначение.

        Returns:
            FullAPIResponse[SuccessApiResponse, YandexApiError]: Результат \
            копирования.
        """
        params = {
            'from': copy_from,
            'path': copy_to
        }
        return self.client.post(
            params=params,
            response_model=SuccessApiResponse,
            url=ye.DISK_COPY
        )  # type: ignore

    def get_file_by_path(
            self,
            path: str
    ) -> FullAPIResponse[FileModel, YandexApiError]:
        """
        Возвращает метаданные файла по пути к нему.

        Args:
            path (str): Путь к файлу на Яндекс-Диске.

        Returns:
            FullAPIResponse[FileModel, YandexApiError]: Метаданные файла.
        """
        params = {'path': path}
        return self.client.get_one(
            params=params,
            response_model=FileModel,
            headers=self.headers,
            url=ye.DISK_RESOURCES
        )  # type: ignore

    def delete_folder_if_exists(self, foldername: str):
        """
        Удаляет папку безвозвратно, если она существует (для очистки в тестах).

        Args:
            foldername (str): Путь/имя папки.
        """
        params = {'path': foldername}
        if self.check_folder_exists(params):
            self.delete_folder(True, params)

    def request_download_link(
            self,
            path_to_file: dict
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        """
        Запрашивает ссылку для скачивания файла.

        Args:
            path_to_file (dict): Параметры с ключом 'path' — путь к файлу.

        Returns:
            FullAPIResponse[SuccessApiResponse, YandexApiError]: Ответ с \
            полем href для скачивания.
        """
        return self.client.get_one(
            response_model=SuccessApiResponse,
            params=path_to_file,
            headers=self.headers,
            url=ye.DISK_DOWNLOAD
        )  # type: ignore

    def download_file(
            self,
            download_link: str,
            filename: str
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        """
        Скачивает файл по ссылке и сохраняет локально.

        Args:
            download_link (str): href из request_download_link.
            filename (str): Имя локального файла для сохранения.

        Returns:
            FullAPIResponse[SuccessApiResponse, YandexApiError]: Результат \
            скачивания.
        """
        response = YandexFileManager.download_file(
            download_link, self.headers, filename
        )
        return response

    def compare_files(
            self,
            local_filename: str,
            downloaded_filename: str
    ):
        """
        Сравнивает содержимое локального и скачанного файлов.

        Args:
            local_filename (str): Путь к исходному файлу.
            downloaded_filename (str): Путь к скачанному файлу.

        Returns:
            tuple[bool, str]: Признак совпадения и поясняющее сообщение.
        """
        return YandexFileManager.compare_files(
            local_filename,
            downloaded_filename
        )

    def get_files_list(
            self,
            params: Optional[dict] = None
    ) -> FullAPIResponse[FilesListModel, YandexApiError]:
        """
        Возвращает плоский список файлов Яндекс-Диска.

        Args:
            params (dict | None): Параметры запроса (например, 'limit').

        Returns:
            FullAPIResponse[FilesListModel, YandexApiError]: Список файлов.
        """
        return self.client.get_one(
            response_model=FilesListModel,
            headers=self.headers,
            params=params,
            url=ye.DISK_FILES
        )  # type: ignore

    def upload(
            self,
            local_path: str,
            remote_path: str
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        """
        Загрузка файла: получает ссылку и грузит файл.

        Args:
            local_path (str): Путь к локальному файлу.
            remote_path (str): Целевой путь на Яндекс-Диске.

        Returns:
            FullAPIResponse[SuccessApiResponse, YandexApiError]: Результат \
            загрузки.

        Raises:
            RuntimeError: Если не удалось получить ссылку для загрузки.
        """
        link = self.request_upload_link({'path': remote_path})
        if link.response_body is None:
            raise RuntimeError(
                f'не удалось прлучить ссылку для загрузки: {remote_path}'
            )
        return self.upload_file(local_path, link.response_body.href)
