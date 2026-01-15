"""Common schemas for pagination and errors."""
from pydantic import BaseModel, Field
from typing import Generic, TypeVar

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: list[T]
    total: int
    limit: int
    offset: int
    has_more: bool


class ErrorResponse(BaseModel):
    """Error response format."""
    error: str
    detail: str | None = None
    code: str


class SuccessResponse(BaseModel):
    """Success response for async operations."""
    status: str = "success"
    message: str | None = None


class BackgroundTaskResponse(BaseModel):
    """Response for background task operations."""
    status: str = "started"
    message: str
