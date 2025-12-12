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


class ActivateRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    code: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")


class ActivateResponseSchema(BaseModel):
    user_id: UUID
    email: EmailStr
    is_active: bool = True
    message: str = "Account activated successfully."


class ResendCodeRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class ResendCodeResponseSchema(BaseModel):
    email: EmailStr
    message: str = "New verification code has been sent"
