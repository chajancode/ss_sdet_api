from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar('T')
E = TypeVar('E')


class WordPressErrorData(BaseModel):
    status: int


class WordPressError(BaseModel):
    code: str
    message: str
    data: WordPressErrorData


class FullAPIResponse(BaseModel, Generic[T, E]):
    status_code: int
    response_body: T | None
    error: Optional[E] = None
