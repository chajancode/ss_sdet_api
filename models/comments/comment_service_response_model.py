from typing import Any, Optional

from pydantic import BaseModel

from models.comments.comments_model import (
                        CommentCreatedOrPatchedResponse,
                        CommentDeletedResponse
                    )
from models.comments.db_record_model import DBCommentData


class CommentsServiceResponse(BaseModel):
    status_code: int
    response_body: CommentCreatedOrPatchedResponse
    db_record: DBCommentData | Any


class CommentsServiceDeleteResponse(BaseModel):
    status_code: int
    response_body: Optional[CommentDeletedResponse] = None
    db_record: Optional[DBCommentData] = None
