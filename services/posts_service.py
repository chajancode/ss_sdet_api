from requests.auth import HTTPBasicAuth

from api.endpoints import WordPressEndpoints as wpe
from api.api_client import APIClient
from dao.posts_dao import PostsDao
from models.posts_model import (
                        PostCreatedOrPatchedResponse,
                        PostDeletedResponse
                    )
from models.posts_service_response_model import (
                        PostsServiceResponse,
                        PostsServiceDeleteResponse
                    )
from utils.tuple_converter import tuple_to_model


class PostsService:
    def __init__(self, auth_data: dict, dao: PostsDao = PostsDao()) -> None:
        self.auth = HTTPBasicAuth(**auth_data)
        self.client = APIClient(wpe.POSTS_ENDPOINT, self.auth)
        self._last_created_id = None
        self.dao = dao

    def create(self, test_data):
        response = self.client.post(test_data, PostCreatedOrPatchedResponse)

        if response.status_code == 201:
            self._last_created_id = response.response_body.id
        return response

    def patch(self, id, test_data):
        return self.client.patch(id, test_data, PostCreatedOrPatchedResponse)

    def delete(self, id, test_data):
        return self.client.delete(id, test_data, PostDeletedResponse)

    def _get_db_record(self, post_id: int | None):
        if post_id is None:
            return None
        return tuple_to_model(
            *self.dao.get_post_by_id(post_id)
        )  # type: ignore

    def check_post_creation(self, test_data: dict):
        response = self.create(test_data)

        return PostsServiceResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=self._get_db_record(self._last_created_id)
        )

    def check_post_patching(self, test_data: dict):
        response = self.patch(self._last_created_id, test_data)

        return PostsServiceResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=self._get_db_record(self._last_created_id)
        )

    def check_post_deletion(self, test_data: dict):
        response = self.delete(self._last_created_id, test_data)

        db_record = self.dao.get_post_by_id(
            self._last_created_id
            ) if self._last_created_id else None
        return PostsServiceDeleteResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=db_record  # type:ignore
        )
