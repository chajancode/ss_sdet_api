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
    def __init__(
            self,
            headers: dict[str, str] | None = None
    ) -> None:
        self.headers = headers
        self.client = APIClient(endpoint=ye.DISK_ENDPOINT, headers=headers)

    def get_authorized_user(self):
        return self.client.get_one(
            response_model=GetUserDataResponse,
            headers=self.headers,
            error_model=None
        )

    def get_unauthorized_user(
            self
    ) -> FullAPIResponse[GetUserDataResponse, YandexApiError]:

        return self.client.get_one(
            response_model=GetUserDataResponse,
            error_model=YandexApiError
        )  # type: ignore

    def create_folder(
            self,
            params: Optional[dict] = None
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:

        return self.client.put(
            response_model=SuccessApiResponse,
            error_model=YandexApiError,
            headers=self.headers,
            params=params,
            url=ye.DISK_RESOURCES
        )  # type: ignore

    def delete_folder(
            self,
            permanently: bool = False,
            params: Optional[dict] = None
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:

        parameters = {'permanently': permanently}
        if params is not None:
            parameters.update(params)
        return self.client.delete(
            response_model=SuccessApiResponse,
            error_model=YandexApiError,
            headers=self.headers,
            params=parameters,
            url=ye.DISK_RESOURCES
        )  # type: ignore

    def folder_in_storage(
            self,
            params: dict
    ) -> FullAPIResponse[FolderModel, YandexApiError]:
        return self.client.get_one(
            params=params,
            error_model=YandexApiError,
            headers=self.headers,
            response_model=FolderModel,
            url=ye.DISK_RESOURCES
            )  # type: ignore

    def is_folder_in_trash(
            self,
            params: dict
    ) -> str | bool:
        items_in_trash = self.client.get_one(
            response_model=TrashModel,
            error_model=YandexApiError,
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
        folder = self.folder_in_storage(params)
        if folder.response_body and \
                folder.response_body.name == params['path']:
            return True
        return False

    def get_folder_name_doesnt_exist(self) -> dict[str, str]:
        while True:
            params = {'path': GenerateRandomTexts.generate_word()}
            if not self.check_folder_exists(params):
                return params

    def _restore(
            self, params: dict
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        return self.client.put(
            response_model=SuccessApiResponse,
            error_model=YandexApiError,
            headers=self.headers,
            params=params,
            url=ye.DISK_TRASH_RESTORE
        )  # type: ignore

    def restore_deleted_folder(
            self,
            params: dict
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        folder_name = self.is_folder_in_trash(params=params)
        return self._restore({'path': folder_name})

    def restore_folder_doesnt_exist(
            self,
            params: dict
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        return self._restore(params=params)

    def empty_trash(self):
        self.client.delete(
            response_model=SuccessApiResponse,
            error_model=YandexApiError,
            headers=self.headers,
            url=ye.DISK_TRASH
        )

    def request_upload_link(
            self,
            params: dict
    ) -> FullAPIResponse[SuccessGetUploadUrl, YandexApiError]:
        return self.client.get_one(
            response_model=SuccessGetUploadUrl,
            error_model=YandexApiError,
            params=params,
            headers=self.headers,
            url=ye.DISK_UPLOAD
        )  # type: ignore

    def upload_file(
            self,
            path_to_local_file: str,
            upload_url: str
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
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
        params = {
            'from': copy_from,
            'path': copy_to
        }
        return self.client.post(
            params=params,
            response_model=SuccessApiResponse,
            error_model=YandexApiError,
            url=ye.DISK_COPY
        )  # type: ignore

    def get_file_by_path(
            self,
            path: str
    ) -> FullAPIResponse[FileModel, YandexApiError]:
        params = {'path': path}
        return self.client.get_one(
            params=params,
            response_model=FileModel,
            error_model=YandexApiError, headers=self.headers,
            url=ye.DISK_RESOURCES
        )  # type: ignore

    def delete_folder_if_exists(self, foldername: str):
        params = {'path': foldername}
        if self.check_folder_exists(params):
            self.delete_folder(True, params)

    def request_download_link(
            self,
            path_to_file: dict
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        return self.client.get_one(
            response_model=SuccessApiResponse,
            error_model=YandexApiError,
            params=path_to_file,
            headers=self.headers,
            url=ye.DISK_DOWNLOAD
        )  # type: ignore

    def download_file(
            self,
            download_link: str,
            filename: str
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        response = YandexFileManager.download_file(
            download_link, self.headers, filename
        )
        return response

    def compare_files(
            self,
            local_filename: str,
            downloaded_filename: str
    ):
        return YandexFileManager.compare_files(
            local_filename,
            downloaded_filename
        )

    def get_files_list(
            self,
            params: Optional[dict] = None
    ) -> FullAPIResponse[FilesListModel, YandexApiError]:
        return self.client.get_one(
            response_model=FilesListModel,
            error_model=YandexApiError,
            headers=self.headers,
            params=params,
            url=ye.DISK_FILES
        )  # type: ignore

    def upload(
            self,
            local_path: str,
            remote_path: str
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:
        link = self.request_upload_link({'path': remote_path})
        if link.response_body is None:
            raise RuntimeError(
                f'не удалось прлучить ссылку для загрузки: {remote_path}'
            )
        return self.upload_file(local_path, link.response_body.href)
