from pydantic import BaseModel
import pytest

from dao.posts_dao import PostsDao
from database.repositories.posts_repository import PostsRepository
from models.posts.api_responses_models import FullAPIResponse, WordPressError
from models.posts.post_create_and_response_dbc import ExpectedPostModel
from models.posts.posts_fixtures_results import FilteredPostsResult
from models.posts.posts_model import PostCreatedOrPatchedResponse
from services.posts_service import PostsService
from utils.data_generators import GenerateExpectedItem as gexp
from utils.dict_creation import group_by_status


@pytest.fixture(scope='session')
def posts_dao(database) -> PostsDao:
    return PostsDao(database=database)


@pytest.fixture(scope='session')
def posts_service(auth_data, posts_dao) -> PostsService:
    return PostsService(auth_data, posts_dao)


@pytest.fixture(scope='session')
def posts_repository(session) -> PostsRepository:
    return PostsRepository(session)


@pytest.fixture(scope='session')
def post_creation_params(request: pytest.FixtureRequest):
    if not hasattr(request, 'param') or request.param is None:
        return {'amount': 1, 'status': 'publish'}
    amount = request.param.get('amount', 5)
    status = request.param.get('status', 'publish')
    return {'amount': amount, 'status': status}


@pytest.fixture(scope='session')
def posts_creation(
    post_creation_params: dict,
    posts_repository: PostsRepository
):
    """
    Создаёт нужное количество постов в БД
    """
    expected_posts = gexp.generate_posts(
                                            **post_creation_params
                                        )
    inserted_posts = posts_repository.create_many(expected_posts)
    yield inserted_posts
    posts_repository.delete_many(list(inserted_posts.keys()))


@pytest.fixture(scope='session')
def get_created_post_via_api(
        posts_service: PostsService,
        posts_creation: dict[int, ExpectedPostModel]
        ) -> dict[
            int, tuple[ExpectedPostModel, FullAPIResponse[
                                PostCreatedOrPatchedResponse, WordPressError]]
            ]:
    result = {}

    for post_id, expected in posts_creation.items():
        response: FullAPIResponse[
            PostCreatedOrPatchedResponse, BaseModel
            ] = posts_service.get_one_post(
            post_id, PostCreatedOrPatchedResponse
        )
        result[post_id] = (expected, response)

    return result


@pytest.fixture(scope='session')
def post_doesnt_exist(posts_service: PostsService):
    response = posts_service.get_one_post(0, PostCreatedOrPatchedResponse)
    return response


@pytest.fixture(scope='function')
def mixed_posts_creation(
            posts_repository: PostsRepository
        ):
    """
    Создаёт 2 поста со статусом 'publish' и 2 поста со статусом 'draft'
    """
    publish_posts = gexp.generate_posts(amount=2, status='publish')
    draft_posts = gexp.generate_posts(amount=2, status='draft')
    all_posts = publish_posts + draft_posts

    inserted_posts = posts_repository.create_many(all_posts)

    grouped_posts: dict[
        str, dict[int, ExpectedPostModel]
    ] = group_by_status(
            list(inserted_posts.keys()),
            list(inserted_posts.values())
        )

    yield grouped_posts

    posts_repository.delete_many(list(inserted_posts.keys()))


@pytest.fixture(scope='function')
def get_filtered_post(
        request: pytest.FixtureRequest,
        posts_service: PostsService,
        mixed_posts_creation: dict[str, dict[int, ExpectedPostModel]]
        ) -> FilteredPostsResult:
    status_to_filter = request.param.get('status')
    posts_expected = mixed_posts_creation.get(status_to_filter, {})
    params = {'status': status_to_filter}
    response = posts_service.get_many_posts(
        PostCreatedOrPatchedResponse, params
    )
    return {
        'expected': posts_expected,
        'response': response,  # type: ignore
        }


@pytest.fixture(scope='session')
def post_create(
        post_creation_params: dict,
        posts_repository: PostsRepository
):
    """
    Создаёт пост для проверки каментов
    """
    post = gexp.generate_posts()[0]
    post_id = posts_repository.create(post)
    yield post_id
    posts_repository.delete(post_id)
