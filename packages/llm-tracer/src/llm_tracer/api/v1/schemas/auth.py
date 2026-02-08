"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema for login request."""

    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """Schema for registration request."""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    username: str
    email: str
    is_admin: bool
