"""User Pydantic models for Controle PGM."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, TypedDict

from pydantic import BaseModel, EmailStr, Field, field_validator

from core.security import sanitize_html


class UserEntity(BaseModel):
    """User entity as stored in Azure Tables."""

    # Azure Tables keys
    PartitionKey: str = "USER"
    RowKey: str  # UUID

    # User fields
    Email: str
    Name: str
    PasswordHash: str
    Role: Literal["admin", "user"] = "user"
    IsActive: bool = True
    MustChangePassword: bool = False
    CreatedAt: datetime
    UpdatedAt: datetime

    model_config = {"from_attributes": True, "extra": "ignore"}


class LoginRequest(BaseModel):
    """Request body for login endpoint."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Response body for successful login."""

    user_id: str
    email: str
    name: str
    role: Literal["admin", "user"]
    must_change_password: bool


class UserCreate(BaseModel):
    """Request body for creating a new user."""

    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    role: Literal["admin", "user"] = "user"

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Sanitize name field."""
        return sanitize_html(v)


class UserUpdate(BaseModel):
    """Request body for updating a user."""

    name: str | None = Field(None, min_length=2, max_length=100)
    role: Literal["admin", "user"] | None = None
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str | None) -> str | None:
        """Sanitize name field."""
        if v is None:
            return None
        return sanitize_html(v)


class UserResponse(BaseModel):
    """User data returned in API responses."""

    id: str
    email: str
    name: str
    role: Literal["admin", "user"]
    is_active: bool
    must_change_password: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: UserEntity) -> UserResponse:
        """Create response from entity."""
        return cls(
            id=entity.RowKey,
            email=entity.Email,
            name=entity.Name,
            role=entity.Role,
            is_active=entity.IsActive,
            must_change_password=entity.MustChangePassword,
            created_at=entity.CreatedAt,
            updated_at=entity.UpdatedAt,
        )


class ChangePasswordRequest(BaseModel):
    """Request body for changing password."""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


class CurrentUser(TypedDict):
    """Current authenticated user info from JWT."""

    user_id: str
    email: str
    name: str
    role: Literal["admin", "user"]
    must_change_password: bool
