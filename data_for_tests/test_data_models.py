from pydantic import BaseModel


class PostTestDataCreate(BaseModel):
    title: str
    content: str
    status: str


class PostTestDataPatch(BaseModel):
    title: str
    content: str


class PostTestDataDelete(BaseModel):
    force: bool


class CommsTestDataCreate(BaseModel):
    content: str
    post: int


class CommsTestDataPatch(BaseModel):
    content: str


class CommsTestDataDelete(BaseModel):
    force: bool
