from typing import Optional

from pydantic import BaseModel


class YandexApiError(BaseModel):
    error: str
    description: str
    message: str
    details: Optional[dict] = None
