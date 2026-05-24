# from requests.auth import HTTPBasicAuth

from api.endpoints import WordPressEndpoints as wpe
# from api.api_client import APIClient
from dao.posts_dao import PostsDao
from models.posts.posts_model import (
                        PostCreatedOrPatchedResponse,
                        PostDeletedResponse
                    )
from models.posts.posts_service_response_model import (
                        PostsServiceDeleteResponse,
                        PostsServiceResponse
                    )
from services.base_service import BaseService
from utils.tuple_converter import tuple_to_post_model
# from utils.tuple_converter import tuple_to_model


class PostsService(BaseService[PostsDao]):
    def __init__(self, auth_data: dict, dao: PostsDao = PostsDao()) -> None:
        super().__init__(auth_data, wpe.POSTS_ENDPOINT, dao)

    def _get_db_record(self, comment_id: int | None):
        if comment_id is None:
            return None
        return tuple_to_post_model(
            *self.dao.get_post_by_id(comment_id)
        )  # type: ignore

    def check_post_creation(self, test_data: dict):
        response = self.create(test_data, PostCreatedOrPatchedResponse)
        return PostsServiceResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=self._get_db_record(self._last_created_id)
        )

    def check_post_patching(self, test_data: dict):
        response = self.patch(
            self._last_created_id, test_data, PostCreatedOrPatchedResponse
        )
        return PostsServiceResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=self._get_db_record(self._last_created_id)
        )

    def check_post_deletion(self, test_data: dict):
        response = self.delete(
            self._last_created_id, test_data, PostDeletedResponse
        )
        db_record = self.dao.get_post_by_id(
            self._last_created_id
            ) if self._last_created_id else None
        return PostsServiceDeleteResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=db_record  # type:ignore
        )
