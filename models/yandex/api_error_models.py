from pydantic import BaseModel


class YandexApiErrorUnauthorized(BaseModel):
    error: str
    description: str
    message: str
