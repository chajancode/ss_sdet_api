from pydantic import BaseModel


class SuccessApiResponse(BaseModel):
    method: str
    href: str
    templated: bool
