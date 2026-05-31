from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseModelIgnoreExtra(BaseModel):
    model_config = ConfigDict(extra='ignore')


class Content(BaseModelIgnoreExtra):
    raw: Optional[str] = None
    rendered: Optional[str]


class CommentCreatedOrPatchedResponse(BaseModelIgnoreExtra):
    id: int
    post: int
    content: Content
    status: str


class CommentDeletedResponse(BaseModel):
    deleted: bool
    previous: CommentCreatedOrPatchedResponse
