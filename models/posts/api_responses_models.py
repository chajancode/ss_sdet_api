from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class FullAPIResponse(BaseModel, Generic[T]):
    status_code: int
    response_body: T | None
