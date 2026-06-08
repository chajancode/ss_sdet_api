from pydantic import BaseModel, ConfigDict


class BaseIgnoreExtra(BaseModel):
    model_config = ConfigDict(extra='ignore')


class UserContent(BaseIgnoreExtra):
    login: str
    display_name: str


class GetUserDataResponseModel(BaseIgnoreExtra):
    user: UserContent
