import pytest

from models.posts.api_responses_models import FullAPIResponse
from models.posts.post_create_and_response_dbc import ExpectedPostModel
from models.posts.posts_fixtures_results import FilteredPostsResult
from models.posts.posts_model import PostCreatedOrPatchedResponse
from utils.string_utils import strip_html


class TestGetPostsFromDB:
    @pytest.mark.parametrize('post_creation_params', [
        {'amount': 5, 'status': 'publish'}
    ], indirect=True)
    def test_get_all_created_posts(
        self, get_created_post_via_api: dict[int, tuple[
            ExpectedPostModel, FullAPIResponse[PostCreatedOrPatchedResponse]]]
    ):

        for post_id, (expected, response) in get_created_post_via_api.items():
            assert response.status_code == 200
            api_post = response.response_body
            assert api_post is not None
            assert strip_html(api_post.title.rendered) == expected.title
            assert strip_html(api_post.content.rendered) == expected.content
            assert api_post.status == expected.status

    @pytest.mark.parametrize('post_creation_params', [
        {'amount': 1, 'status': 'publish'}
    ], indirect=True)
    def test_get_post_by_id(
        self, get_created_post_via_api: dict[int, tuple[
            ExpectedPostModel, FullAPIResponse[PostCreatedOrPatchedResponse]]]
    ):
        for post_id, (expected, response) in get_created_post_via_api.items():
            assert response.status_code == 200
            api_post = response.response_body
            assert api_post is not None
            assert strip_html(api_post.title.rendered) == expected.title
            assert strip_html(api_post.content.rendered) == expected.content
            assert api_post.status == expected.status

    def test_get_post_not_exists(
            self,
            post_doesnt_exist: FullAPIResponse[PostCreatedOrPatchedResponse]
    ):
        assert post_doesnt_exist.error is not None
        assert post_doesnt_exist.status_code == 404
        assert post_doesnt_exist.error.code == 'rest_post_invalid_id'
        assert post_doesnt_exist.error.message == 'Неверный ID записи.'
        assert post_doesnt_exist.error.data.status == 404

    @pytest.mark.parametrize('get_filtered_post', [
        {'status': 'publish'},
        {'status': 'draft'}
    ], indirect=True
                             )
    def test_get_post_by_status(
        self,
        get_filtered_post: FilteredPostsResult
    ):
        expected_dict = get_filtered_post['expected']
        response = get_filtered_post['response']

        assert response.status_code == 200
        api_posts = response.response_body
        assert api_posts is not None

        api_by_id = {p.id: p for p in api_posts}
        for post_id, exp in expected_dict.items():
            assert post_id in api_by_id, f"Ппост с id {post_id} не найден"
            api_post = api_by_id[post_id]
            assert strip_html(api_post.title.rendered) == exp.title
            assert strip_html(api_post.content.rendered) == exp.content
