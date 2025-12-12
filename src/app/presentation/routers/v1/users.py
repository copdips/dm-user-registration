"""Users router"""

from fastapi import APIRouter, status

from app.application.dto.user_dto import (
    RegisterUserRequest,
)
from app.domain import Email, Password
from app.presentation.dependencies import (
    register_user_use_case,
)
from app.presentation.schemas.users import (
    RegisterRequestSchema,
    RegisterResponseSchema,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(request: RegisterRequestSchema) -> RegisterResponseSchema:
    """Register a new user"""
    use_case = register_user_use_case()

    dto = RegisterUserRequest(Email(request.email), Password.create(request.password))
    result = await use_case.execute(dto)

    return RegisterResponseSchema(
        user_id=result.user_id.value,
        email=result.email.value,
        message=result.message,
    )
