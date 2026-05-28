from typing import Any, Optional

from pydantic import BaseModel

from models.posts.db_record_model import DBPostData
from models.posts.posts_model import (
    PostCreatedOrPatchedResponse,
    PostDeletedResponse
    )


class PostsServiceResponse(BaseModel):
    status_code: int
    response_body: PostCreatedOrPatchedResponse
    db_record: DBPostData | Any


class PostsServiceDeleteResponse(BaseModel):
    status_code: int
    response_body: Optional[PostDeletedResponse] = None
    db_record: Optional[DBPostData] = None
