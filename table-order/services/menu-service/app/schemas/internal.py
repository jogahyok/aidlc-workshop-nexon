from pydantic import BaseModel


class OptionValidation(BaseModel):
    id: int
    name: str
    price: int


class OptionGroupValidation(BaseModel):
    id: int
    name: str
    type: str
    is_required: bool
    max_select: int | None
    options: list[OptionValidation]


class MenuValidationResponse(BaseModel):
    menu_id: int
    name: str
    price: int
    is_available: bool
    option_groups: list[OptionGroupValidation]
