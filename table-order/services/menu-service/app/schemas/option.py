from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class OptionItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    price: int = Field(..., ge=0)
    sort_order: Optional[int] = None


class OptionItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[int] = Field(None, ge=0)


class OptionItemResponse(BaseModel):
    id: int
    option_group_id: int
    name: str
    price: int
    sort_order: int
    created_at: datetime
    updated_at: datetime


class OptionGroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    type: str = Field(..., pattern="^(radio|checkbox)$")
    max_select: Optional[int] = Field(None, ge=1)
    sort_order: Optional[int] = None
    items: list[OptionItemCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_type_constraints(self):
        if self.type == "radio":
            self.max_select = 1
        return self


class OptionGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    type: Optional[str] = Field(None, pattern="^(radio|checkbox)$")
    max_select: Optional[int] = Field(None, ge=1)


class OptionGroupResponse(BaseModel):
    id: int
    menu_item_id: int
    name: str
    type: str
    is_required: bool
    max_select: Optional[int]
    sort_order: int
    items: list[OptionItemResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
