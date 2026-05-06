from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: list
    pagination: "PaginationMeta"


class PaginationMeta(BaseModel):
    page: int
    size: int
    total_items: int
    total_pages: int
