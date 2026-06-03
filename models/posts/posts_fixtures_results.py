from typing import TypedDict
from models.posts.post_create_and_response_dbc import ExpectedPostModel
from models.posts.api_responses_models import FullAPIResponse
from models.posts.posts_model import PostCreatedOrPatchedResponse


class FilteredPostsResult(TypedDict):
    expected: dict[int, ExpectedPostModel]
    response: FullAPIResponse[list[PostCreatedOrPatchedResponse]]
