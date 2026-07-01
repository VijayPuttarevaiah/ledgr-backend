import uuid

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    colour: str
    icon: str
    is_default: bool

    model_config = {"from_attributes": True}
