import pytest

from dao.comments_dao import CommentsDao
from database.database_session import DatabaseSession
from database.repositories.comments_repository import CommentsRepository
from models.comments.comments_fixtures_results import FilteredCommsResult
from models.comments.comments_model import CommentCreatedOrPatchedResponse
from models.comments.comms_create_and_response_dbc import ExpectedCommModel
from models.posts.api_responses_models import FullAPIResponse
from services.comments_service import CommentsService
from utils.data_generators import GenerateExpectedItem as gexp
from utils.dict_creation import group_by_status


@pytest.fixture(scope='session')
def comments_dao(database):
    return CommentsDao(database=database)


@pytest.fixture(scope='session')
def comments_service(auth_data, comments_dao):
    return CommentsService(auth_data, comments_dao)


@pytest.fixture(scope='session')
def comments_repository(session):
    return CommentsRepository(session)


@pytest.fixture(scope='session')
def comment_creation_params(request: pytest.FixtureRequest) -> dict:
    amount = request.param.get('amount', 5)
    user_id = request.param.get('user_id', '1')
    comment_author = request.param.get('author', 'chajan')
    status = request.param.get('approved', 'approved')
    return {
        'amount': amount,
        'user_id': user_id,
        'author': comment_author,
        'status': status
        }


@pytest.fixture(scope='session')
def comments_creation(
    comments_repository: CommentsRepository,
    post_create: int,
    comment_creation_params: dict
):
    expected_comms = gexp.generate_comms(
        post_create,
        comment_creation_params['amount'],
        comment_creation_params['status']
    )
    inserted_comms = comments_repository.create_many(
        expected_comms,
        comment_creation_params['author'],
        comment_creation_params['user_id']
    )
    yield inserted_comms

    comments_repository.delete_many(list(inserted_comms.keys()))


@pytest.fixture(scope='session')
def get_created_comms_via_api(
        comments_service: CommentsService,
        comments_creation: dict[int, ExpectedCommModel]
        ) -> dict[
            int, tuple[ExpectedCommModel, FullAPIResponse[
                                CommentCreatedOrPatchedResponse]]
        ]:
    result = {}
    for comm_id, expected in comments_creation.items():
        response: FullAPIResponse[
            CommentCreatedOrPatchedResponse
            ] = comments_service.get_one(
                comm_id, CommentCreatedOrPatchedResponse
            )
        result[comm_id] = (expected, response)

    return result


@pytest.fixture(scope='session')
def single_comment_creation(
        session: DatabaseSession,
        post_create: int,
        comment_creation_params: dict,
        comments_repository: CommentsRepository
):
    expected: ExpectedCommModel = gexp.generate_comms(
        post_create, 1, 'approved')[0]

    inserted_comm = {}

    comm_id = comments_repository.create(
        expected,
        comment_creation_params['author'],
        comment_creation_params['user_id']
    )
    inserted_comm[comm_id] = expected
    yield inserted_comm

    comments_repository.delete(comm_id)


@pytest.fixture(scope='session')
def get_single_comm_via_api(
        comments_service: CommentsService,
        single_comment_creation: dict[int, ExpectedCommModel]
) -> tuple[int, ExpectedCommModel,
           FullAPIResponse[CommentCreatedOrPatchedResponse]]:

    comm_id, expected = next(iter(single_comment_creation.items()))

    response = comments_service.get_one(
        comm_id, CommentCreatedOrPatchedResponse
    )
    return (comm_id, expected, response)


@pytest.fixture(scope='session')
def comm_doesnt_exist(comments_service: CommentsService):
    response = comments_service.get_one(0, CommentCreatedOrPatchedResponse)
    return response


@pytest.fixture(scope='function')
def mixed_comms_creation(
            session: DatabaseSession,
            post_create: int,
            comment_creation_params: dict,
            comments_repository: CommentsRepository
        ):
    """
    Создаёт 2 коммента со статусом 'approved' и 2 коммента со статусом 'trash'
    """
    approved_comms = gexp.generate_comms(
        post_create, amount=2, status='approved'
    )
    trash_comms = gexp.generate_comms(post_create, amount=2, status='trash')
    all_comms = approved_comms + trash_comms

    inserted_comms = comments_repository.create_many(
        all_comms,
        comment_creation_params['author'],
        comment_creation_params['user_id']
    )

    grouped_comms: dict[
        str, dict[int, ExpectedCommModel]
    ] = group_by_status(list(inserted_comms.keys()), all_comms)

    yield grouped_comms

    comments_repository.delete_many(list(inserted_comms.keys()))


@pytest.fixture(scope='function')
def get_filtered_comm(
        request: pytest.FixtureRequest,
        comments_service: CommentsService,
        mixed_comms_creation: dict[str, dict[int, ExpectedCommModel]]
        ) -> FilteredCommsResult:
    """
    Делает запрос в API с фильтрацией коментариев по статусу.
    """
    status_to_filter = request.param.get('status')
    comm_expected = mixed_comms_creation.get(status_to_filter, {})
    params = {'status': status_to_filter}
    response = comments_service.get_many(
        CommentCreatedOrPatchedResponse, params
    )
    return {
        'expected': comm_expected,
        'response': response,
        }
