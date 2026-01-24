"""
Common Pydantic Schemas

Shared schemas used across multiple API endpoints.
"""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
from datetime import datetime

# Generic type for paginated responses
T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
    success: bool = True
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    service: str
    timestamp: datetime = None

    class Config:
        from_attributes = True


class BulkOperationResponse(BaseModel):
    """Response for bulk operations."""
    success_count: int
    error_count: int
    errors: Optional[List[dict]] = None
    message: str
