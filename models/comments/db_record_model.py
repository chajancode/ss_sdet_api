from pydantic import BaseModel


class DBCommentData(BaseModel):
    post: int
    content: str
