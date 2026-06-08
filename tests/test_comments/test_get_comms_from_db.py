import pytest

from models.comments.comments_fixtures_results import FilteredCommsResult
from models.comments.comments_model import CommentCreatedOrPatchedResponse
from models.comments.comms_create_and_response_dbc import ExpectedCommModel
from models.posts.api_responses_models import FullAPIResponse, WordPressError
from utils.string_utils import strip_html


class TestGetCommsFromDB:

    @pytest.mark.parametrize('post_creation_params, comment_creation_params', [
        (
            {'amount': 1, 'status': 'publish'},
            {'amount': 5, 'user_id': 1,
             'comment_author': 'chajan', 'status': 'approved'}
        )
    ], indirect=True)
    def test_all_created_comms(
        self, get_created_comms_via_api: dict[int, tuple[
            ExpectedCommModel, FullAPIResponse[
                            CommentCreatedOrPatchedResponse, WordPressError]]]
    ):
        for comm_id, (expected, response) in get_created_comms_via_api.items():
            assert response.status_code == 200
            api_comm = response.response_body
            assert api_comm is not None
            assert strip_html(api_comm.content.rendered) == expected.content
            assert api_comm.post == expected.post_id
            assert api_comm.status == expected.status

    @pytest.mark.parametrize('post_creation_params, comment_creation_params', [
        (
            {'amount': 1, 'status': 'publish'},
            {'amount': 1, 'user_id': 1,
             'comment_author': 'chajan', 'status': 'approved'}
        )
    ], indirect=True)
    def test_get_comm_by_id(
        self,
        get_single_comm_via_api: tuple[int, ExpectedCommModel, FullAPIResponse[
             CommentCreatedOrPatchedResponse, WordPressError]]
    ):
        assert len(get_single_comm_via_api) == 3
        id, expected, response = get_single_comm_via_api
        assert response.status_code == 200
        assert response.response_body is not None
        assert response.response_body.id == id
        assert response.response_body.post == expected.post_id
        assert strip_html(
            response.response_body.content.rendered
                                            ) == expected.content
        assert response.response_body.status == expected.status

    def test_get_comm_not_exists(
            self,
            comm_doesnt_exist: FullAPIResponse[
                CommentCreatedOrPatchedResponse, WordPressError]
    ):
        assert comm_doesnt_exist.error is not None
        assert comm_doesnt_exist.status_code == 404
        assert comm_doesnt_exist.error.code == 'rest_comment_invalid_id'
        assert comm_doesnt_exist.error.message == 'Неверный ID комментария.'
        assert comm_doesnt_exist.error.data.status == 404

    @pytest.mark.parametrize(
        'post_creation_params, get_filtered_comm, comment_creation_params', [(
            {'amount': 1, 'status': 'publish'},
            {'status': 'approved'},
            {'amount': 1, 'user_id': 1, 'comment_author': 'chajan',
                'status': 'approved'}),
            ({'amount': 1, 'status': 'publish'},
                {'status': 'trash'},
                {'amount': 1, 'user_id': 1, 'comment_author': 'chajan',
                    'status': 'approved'})
        ], indirect=True)
    def test_get_comm_by_status(
        self,
        get_filtered_comm: FilteredCommsResult
    ):
        expected_dict = get_filtered_comm['expected']
        response = get_filtered_comm['response']

        assert response.status_code == 200
        api_comms = response.response_body
        assert api_comms is not None

        api_by_id = {c.id: c for c in api_comms}
        for comm_id, expected in expected_dict.items():
            assert comm_id in api_by_id, f"камент с id {comm_id} не найден"
            api_comm = api_by_id[comm_id]
            assert api_comm.post == expected.post_id
            assert strip_html(api_comm.content.rendered) == expected.content
            assert api_comm.status == expected.status
