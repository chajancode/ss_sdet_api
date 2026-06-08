from typing import TypedDict

from models.comments.comments_model import CommentCreatedOrPatchedResponse
from models.comments.comms_create_and_response_dbc import ExpectedCommModel
from models.posts.api_responses_models import FullAPIResponse, WordPressError


class CommsExpectedAndResponseResult(TypedDict):
    expected: dict[int, ExpectedCommModel]
    response: FullAPIResponse[
        list[CommentCreatedOrPatchedResponse], WordPressError
        ]


class FilteredCommsResult(TypedDict):
    expected: dict[int, ExpectedCommModel]
    response: FullAPIResponse[
        list[CommentCreatedOrPatchedResponse], WordPressError
        ]
