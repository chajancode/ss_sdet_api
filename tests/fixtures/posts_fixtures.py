import pytest

from dao.posts_dao import PostsDao
from database_session import DatabaseSession
from models.posts.api_responses_models import FullAPIResponse
from models.posts.post_create_and_response_dbc import ExpectedPostModel
from models.posts.posts_fixtures_results import FilteredPostsResult
from models.posts.posts_model import PostCreatedOrPatchedResponse
from services.posts_service import PostsService
from utils.data_generators import GenerateExpectedItem as gexp
from utils.dict_creation import group_by_status
from utils.string_utils import to_slug


@pytest.fixture(scope='session')
def posts_dao(database) -> PostsDao:
    return PostsDao(database=database)


@pytest.fixture(scope='session')
def posts_service(auth_data, posts_dao) -> PostsService:
    return PostsService(auth_data, posts_dao)


@pytest.fixture(scope='session')
def post_creation_params(request: pytest.FixtureRequest):
    if not hasattr(request, 'param') or request.param is None:
        return {'amount': 1, 'status': 'publish'}
    amount = request.param.get('amount', 5)
    status = request.param.get('status', 'publish')
    return {'amount': amount, 'status': status}


@pytest.fixture(scope='session')
def posts_creation(session: DatabaseSession, post_creation_params: dict):
    """
    Создаёт нужное количество постов в БД
    """
    expected_posts = gexp.generate_posts(
                                            **post_creation_params
                                        )
    posts_ids = []
    for post in expected_posts:

        query = """
        INSERT INTO wp_posts(
        post_author, post_date, post_date_gmt, post_content, post_title,
        post_excerpt, post_status, post_name, to_ping, pinged, post_modified,
        post_modified_gmt, post_content_filtered, post_type
        ) VALUES (
        %s, NOW(), NOW(), %s, %s, '', %s, %s, '', '', NOW(), NOW(), '', %s
        )
        """
        params = (
            1, post.content, post.title, post.status,
            to_slug(post.title), 'post'
        )
        post_id = session.execute(query, params)
        posts_ids.append(post_id)

    inserted_posts: dict[int, ExpectedPostModel] = {
            post_id: post for post_id, post in zip(posts_ids, expected_posts)
        }

    yield inserted_posts

    for post_id in inserted_posts:
        session.execute(
            'DELETE FROM wp_posts WHERE ID = %s', (post_id,)
        )


@pytest.fixture(scope='session')
def get_created_post_via_api(
        posts_service: PostsService,
        posts_creation: dict[int, ExpectedPostModel]
        ) -> dict[
            int, tuple[ExpectedPostModel, FullAPIResponse[
                                PostCreatedOrPatchedResponse]]
            ]:
    result = {}

    for post_id, expected in posts_creation.items():
        response: FullAPIResponse[
            PostCreatedOrPatchedResponse
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
            session: DatabaseSession
        ):
    """
    Создаёт 2 поста со статусом 'publish' и 2 поста со статусом 'draft'
    """
    publish_posts = gexp.generate_posts(amount=2, status='publish')
    draft_posts = gexp.generate_posts(amount=2, status='draft')
    all_posts = publish_posts + draft_posts

    post_ids = []
    for post in all_posts:
        query = """
        INSERT INTO wp_posts(
        post_author, post_date, post_date_gmt, post_content, post_title,
        post_excerpt, post_status, post_name, to_ping, pinged, post_modified,
        post_modified_gmt, post_content_filtered, post_type
        ) VALUES (
        %s, NOW(), NOW(), %s, %s, '', %s, %s, '', '', NOW(), NOW(), '', %s
        )
        """
        params = (
            1, post.content, post.title, post.status,
            to_slug(post.title), 'post'
        )
        post_id = session.execute(query, params)
        post_ids.append(post_id)

    inserted_posts: dict[
        str, dict[int, ExpectedPostModel]
    ] = group_by_status(post_ids, all_posts)

    yield inserted_posts

    for post_id in post_ids:
        session.execute(
            "DELETE FROM wp_posts WHERE ID = %s", (post_id,)
        )


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
        'response': response,
        }


@pytest.fixture(scope='session')
def post_create(session: DatabaseSession, post_creation_params: dict):
    """
    Создаёт пост для проверки каментов
    """
    post = gexp.generate_posts()[0]

    query = """
    INSERT INTO wp_posts(
    post_author, post_date, post_date_gmt, post_content, post_title,
    post_excerpt, post_status, post_name, to_ping, pinged, post_modified,
    post_modified_gmt, post_content_filtered, post_type
    ) VALUES (
    %s, NOW(), NOW(), %s, %s, '', %s, %s, '', '', NOW(), NOW(), '', %s
    )
    """
    params = (
        1, post.content, post.title, post.status,
        to_slug(post.title), 'post'
    )
    post_id = session.execute(query, params)

    yield post_id

    session.execute(
        'DELETE FROM wp_posts WHERE ID = %s', (post_id,)
    )
