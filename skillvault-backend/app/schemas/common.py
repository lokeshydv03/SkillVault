from typing import Any, Generic, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    pages: int


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
