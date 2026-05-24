from typing import Any

from pydantic import BaseModel

from models.db_record_model import DBPostData
from models.posts_model import (
    PostCreatedOrPatchedResponse,
    PostDeletedResponse
    )


class PostsServiceResponse(BaseModel):
    status_code: int
    response_body: PostCreatedOrPatchedResponse
    db_record: DBPostData | Any


class PostsServiceDeleteResponse(BaseModel):
    status_code: int
    response_body: PostDeletedResponse
    db_record: DBPostData | Any
