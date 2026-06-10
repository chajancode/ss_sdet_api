from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ResourceModel(BaseModel):
    path: str
    type: str
    name: str
    model_config = ConfigDict(extra='ignore')


class TrashItem(BaseModel):
    name: str
    type: str
    path: str
    model_config = ConfigDict(extra='ignore')


class Embedded(BaseModel):
    items: list[TrashItem]
    model_config = ConfigDict(extra='ignore')


class TrashModel(BaseModel):
    embedded: Optional[Embedded] = Field(None, alias='_embedded')
    model_config = ConfigDict(extra='ignore')
