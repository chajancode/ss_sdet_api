from pydantic import BaseModel


class PostCreateDBCModel(BaseModel):

    post_content: str
    post_title: str


class ExpectedPostModel(BaseModel):
    title: str
    content: str
    status: str
