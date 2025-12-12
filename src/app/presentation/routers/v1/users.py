"""Users router"""

from fastapi import APIRouter, status

from app.application.dto.user_dto import (
    ActivateUserRequest,
    RegisterUserRequest,
)
from app.domain import Email, Password, VerificationCode
from app.presentation.dependencies import (
    activate_user_use_case,
    register_user_use_case,
)
from app.presentation.schemas.users import (
    ActivateRequestSchema,
    ActivateResponseSchema,
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


@router.post(
    "/activate",
    status_code=status.HTTP_200_OK,
    summary="Activate user account",
)
async def activate_user(
    request: ActivateRequestSchema,
) -> ActivateResponseSchema:
    """Activate user account"""
    use_case = activate_user_use_case()

    dto = ActivateUserRequest(
        email=Email(request.email),
        password=request.password,
        code=VerificationCode(request.code),
    )
    result = await use_case.execute(dto)

    return ActivateResponseSchema(
        user_id=result.user_id.value,
        email=result.email.value,
        is_active=result.is_active,
    )
