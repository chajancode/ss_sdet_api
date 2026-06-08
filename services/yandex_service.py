from models.posts.api_responses_models import FullAPIResponse
from models.yandex.api_error_models import YandexApiErrorUnauthorized
from models.yandex.get_user_data_model import GetUserDataResponseModel
from services.base_service import BaseService


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

    def get_authorized_user(self):
        return self.client.get_one(
            response_model=GetUserDataResponseModel,
            headers=self.headers,
        )

    def get_unauthorized_user(
            self
    ) -> FullAPIResponse[GetUserDataResponseModel, YandexApiErrorUnauthorized]:
        return self.client.get_one(
            response_model=GetUserDataResponseModel,
            error_model=YandexApiErrorUnauthorized
        )  # type: ignore
