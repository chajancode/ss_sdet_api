import pytest

from data_for_tests.test_data_creator import data_creator
from data_for_tests.test_data_models import (
                            CommsTestDataCreate,
                            CommsTestDataDelete,
                            CommsTestDataPatch
                        )
from services.comments_service import CommentsService


class TestInteractWithComments:
    @pytest.mark.parametrize(
            'comm_create', data_creator('comms_create')
    )
    def test_post_creation(
            self, comments_service: CommentsService,
            comm_create: CommsTestDataCreate,
            post_create: int
    ):
        comm_create.post = post_create
        res = comments_service.check_comment_creation(comm_create.model_dump())
        assert res.status_code == 201
        assert res.response_body.content.raw == comm_create.content
        assert res.response_body.post == comm_create.post
        assert res.db_record.content == comm_create.content
        assert res.db_record.post == comm_create.post

    @pytest.mark.parametrize(
            'comm_patch', data_creator('comms_patch')
    )
    def test_post_patching(
            self, comments_service: CommentsService,
            comm_patch: CommsTestDataPatch
    ):
        res = comments_service.check_comment_patching(comm_patch.model_dump())
        assert res.status_code == 200
        assert res.response_body.id
        assert res.response_body.post
        assert res.response_body.content.raw == comm_patch.content
        assert res.db_record.content == comm_patch.content

    @pytest.mark.parametrize(
            'comm_delete', data_creator('comms_delete')
    )
    def test_post_deletion(
            self, comments_service: CommentsService,
            comm_delete: CommsTestDataDelete
    ):
        res = comments_service.check_comment_deletion(comm_delete.model_dump())
        assert res.status_code == 200
        assert res.response_body.deleted is True  # type: ignore
        assert res.response_body.previous  # type: ignore
        assert not res.db_record
        res = comments_service.check_comment_deletion(comm_delete.model_dump())
        assert res.status_code == 404
