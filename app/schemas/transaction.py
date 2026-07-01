import uuid
from datetime import date as date_type, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TransactionCreate(BaseModel):
    model_config = {"extra": "forbid"}

    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    type: Literal["expense", "income"]
    date: date_type
    category_id: uuid.UUID
    vendor: str | None = Field(default=None, max_length=120)
    payment_method: str | None = Field(default=None, max_length=60)
    note: str | None = Field(default=None, max_length=500)
    receipt_url: str | None = Field(default=None, max_length=255)

    @field_validator("date")
    @classmethod
    def date_not_in_future(cls, value: date_type) -> date_type:
        if value > date_type.today():
            raise ValueError("date cannot be in the future")
        return value


class CategoryBrief(BaseModel):
    id: uuid.UUID
    name: str
    colour: str

    model_config = {"from_attributes": True}


class TransactionResponse(BaseModel):
    id: uuid.UUID
    amount: Decimal
    type: str
    date: date_type
    category: CategoryBrief
    vendor: str | None
    payment_method: str | None
    note: str | None
    receipt_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    page: int
    page_size: int
    total_items: int
    total_pages: int
