"""API request/response schemas."""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class RegisterResponseSchema(BaseModel):
    user_id: UUID
    email: EmailStr
    message: str = (
        "User registered. "
        "Please check your email for verification code to activate your account."
    )
