from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class WordPressErrorData(BaseModel):
    status: int


class WordPressError(BaseModel):
    code: str
    message: str
    data: WordPressErrorData


class FullAPIResponse(BaseModel, Generic[T]):
    status_code: int
    response_body: T | None
    error: Optional[WordPressError]
