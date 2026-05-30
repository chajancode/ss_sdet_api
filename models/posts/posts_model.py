from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseModelIgnoreExtra(BaseModel):
    model_config = ConfigDict(extra='ignore')


class Title(BaseModelIgnoreExtra):
    raw: Optional[str] = None
    rendered: Optional[str] = None


class Content(BaseModelIgnoreExtra):
    raw: Optional[str] = None
    rendered: Optional[str] = None


class PostCreatedOrPatchedResponse(BaseModelIgnoreExtra):
    id: int
    status: str
    title: Title
    content: Content


class PostDeletedResponse(BaseModel):
    deleted: bool
    previous: PostCreatedOrPatchedResponse


class PostReDeletionResponse(BaseModel):
    code: str
    message: str
    data: dict
