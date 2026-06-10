from typing import Optional

from api.api_client import APIClient
from api.endpoints import YandexEndpoints
from models.posts.api_responses_models import FullAPIResponse
from models.yandex.api_error_models import YandexApiError
from models.yandex.success_api_response_models import SuccessApiResponse
from models.yandex.resource_models import ResourceModel, TrashModel
from models.yandex.get_user_data_model import GetUserDataResponse
from services.base_service import BaseService
from utils.data_extraction import extract_deleted_folder_path_from_trash
from utils.data_generators import GenerateRandomTexts


class YandexService(BaseService):
    def __init__(
            self,
            endpoint: str,
            headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(
            endpoint=endpoint,
            headers=headers,
            auth_data=None
        )
        self.resources = YandexEndpoints.DISK_RESOURCES
        self.trash = YandexEndpoints.DISK_TRASH
        self.restore = YandexEndpoints.DISK_TRASH_RESTORE

        self.resources_client = APIClient(self.resources, headers=headers)
        self.trash_client = APIClient(self.trash, headers=headers)
        self.restore_client = APIClient(self.restore, headers=headers)

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

        return self.resources_client.put(
            response_model=SuccessApiResponse,
            error_model=YandexApiError,
            headers=self.headers,
            params=params
        )  # type: ignore

    def delete_folder(
            self,
            permanently: bool = False,
            params: Optional[dict] = None
    ) -> FullAPIResponse[SuccessApiResponse, YandexApiError]:

        parameters = {'permanently': permanently}

        if params is not None:
            parameters.update(params)

        return self.resources_client.delete(
            response_model=SuccessApiResponse,
            error_model=YandexApiError,
            headers=self.headers,
            params=parameters
        )  # type: ignore

    def folder_in_storage(
            self,
            params: dict
    ) -> FullAPIResponse[ResourceModel, YandexApiError]:
        return self.resources_client.get_one(
            params=params,
            error_model=YandexApiError,
            headers=self.headers,
            response_model=ResourceModel
            )  # type: ignore

    def is_folder_in_trash(
            self,
            params: dict
    ) -> str | bool:
        items_in_trash = self.trash_client.get_one(
            response_model=TrashModel,
            error_model=YandexApiError,
            headers=self.headers
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
        return self.restore_client.put(
            response_model=SuccessApiResponse,
            error_model=YandexApiError,
            headers=self.headers,
            params=params
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
        self.trash_client.get_one(
            response_model=SuccessApiResponse,
            error_model=YandexApiError
        )
