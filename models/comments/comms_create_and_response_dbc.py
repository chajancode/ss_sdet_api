from pydantic import BaseModel


class ExpectedCommModel(BaseModel):
    post_id: int
    content: str
    status: str
