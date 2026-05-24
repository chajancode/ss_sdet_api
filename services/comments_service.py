from api.endpoints import WordPressEndpoints as wpe
from dao.comments_dao import CommentsDao
from models.comments.comment_service_response_model import (
                        CommentsServiceDeleteResponse,
                        CommentsServiceResponse
                    )
from models.comments.comments_model import (
                        CommentCreatedOrPatchedResponse,
                        CommentDeletedResponse
                    )
from services.base_service import BaseService
from utils.tuple_converter import tuple_to_comm_model


class CommentsService(BaseService[CommentsDao]):
    def __init__(
            self, auth_data: dict, dao: CommentsDao = CommentsDao()
            ) -> None:
        super().__init__(auth_data, wpe.COMMENTS_ENDPOINT, dao)

    # def create(self, test_data):
    #     response = self.client.post(test_data, PostCreatedOrPatchedResponse)

    #     if response.status_code == 201:
    #         self._last_created_id = response.response_body.id
    #     return response

    # def patch(self, id, test_data):
    #     return self.client.patch(id, test_data, PostCreatedOrPatchedResponse)

    # def delete(self, id, test_data):
    #     return self.client.delete(id, test_data, PostDeletedResponse)

    # def _get_db_record(self, post_id: int | None):
    #     if post_id is None:
    #         return None
    #     return tuple_to_model(
    #         *self.dao.get_post_by_id(post_id)
    #     )  # type: ignore
    def _get_db_record(self, comment_id: int | None):
        if comment_id is None:
            return None
        return tuple_to_comm_model(
            *self.dao.get_comment_by_id(comment_id)
        )  # type: ignore

    def check_comment_creation(self, test_data: dict):
        response = self.create(test_data, CommentCreatedOrPatchedResponse)

        return CommentsServiceResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=self._get_db_record(self._last_created_id)
        )

    def check_comment_patching(self, test_data: dict):
        response = self.patch(
            self._last_created_id, test_data, CommentCreatedOrPatchedResponse
        )

        return CommentsServiceResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=self._get_db_record(self._last_created_id)
        )

    def check_comment_deletion(self, test_data: dict):
        response = self.delete(
            self._last_created_id, test_data, CommentDeletedResponse
        )

        db_record = self.dao.get_comment_by_id(
            self._last_created_id
            ) if self._last_created_id else None
        return CommentsServiceDeleteResponse(
            status_code=response.status_code,
            response_body=response.response_body,
            db_record=db_record  # type:ignore
        )
