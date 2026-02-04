from typing import Any
from fastapi import HTTPException, status


class DuplicateResourceError(HTTPException):
    """Raised when attempting to create a resource that already exists."""
    
    def __init__(self, resource: str, detail: str | None = None):
        message = detail or f"{resource} already exists"
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )


class ResourceNotFoundError(HTTPException):
    """Raised when a requested resource cannot be found."""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with identifier '{identifier}' not found"
        )


class ValidationError(HTTPException):
    """Raised when request validation fails."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
