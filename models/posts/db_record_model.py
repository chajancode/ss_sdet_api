from pydantic import BaseModel


class DBPostData(BaseModel):
    title: str
    content: str
    status: str
