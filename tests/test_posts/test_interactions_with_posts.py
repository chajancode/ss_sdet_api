import pytest

from services.posts_service import PostsService
from data_for_tests.test_data_creator import data_creator
from data_for_tests.test_data_models import (
                                PostTestDataCreate,
                                PostTestDataDelete,
                                PostTestDataPatch
                            )


class TestInteractWithPosts:
    @pytest.mark.parametrize(
            'post_create', data_creator('post_create')
    )
    def test_post_creation(
            self, posts_service: PostsService, post_create: PostTestDataCreate
    ):
        res = posts_service.check_post_creation(post_create.model_dump())
        assert res.status_code == 201
        assert res.response_body.title.raw == post_create.title
        assert res.response_body.content.raw == post_create.content
        assert res.response_body.status == post_create.status
        assert res.db_record.title == post_create.title
        assert res.db_record.content == post_create.content
        assert res.db_record.status == post_create.status

    @pytest.mark.parametrize(
            'post_patch', data_creator('post_patch')
    )
    def test_post_patching(
            self,
            posts_service: PostsService,
            post_patch: PostTestDataPatch,
            post_create: int
    ):
        res = posts_service.check_post_patching(
            post_create, post_patch.model_dump()
        )
        assert res.status_code == 200
        assert res.response_body.title.raw == post_patch.title
        assert res.response_body.content.raw == post_patch.content
        assert res.db_record.title == post_patch.title
        assert res.db_record.content == post_patch.content

    @pytest.mark.parametrize(
            'post_delete', data_creator('post_delete')
    )
    def test_post_deletion(
            self,
            posts_service: PostsService,
            post_delete: PostTestDataDelete,
            post_create: int
    ):
        res = posts_service.check_post_deletion(
            post_create, post_delete.model_dump()
        )
        assert res.status_code == 200
        assert res.response_body.deleted is True  # type: ignore
        assert not res.db_record
        res = posts_service.check_post_deletion(
            post_create, post_delete.model_dump()
        )
        assert res.status_code == 404
