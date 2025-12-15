"""Users router"""

from fastapi import APIRouter, status

from app.application.dto.user_dto import (
    ActivateUserRequest,
    RegisterUserRequest,
    ResendCodeRequest,
)
from app.domain import Email, Password, VerificationCode
from app.presentation.dependencies import (
    ActivateUserUseCaseDep,
    HTTPEmailPasswordBasicCredentialsDep,
    RegisterUserUseCaseDep,
    ResendCodeUseCaseDep,
)
from app.presentation.schemas.users import (
    ActivateRequestSchema,
    ActivateResponseSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
    ResendCodeResponseSchema,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    request: RegisterRequestSchema, use_case: RegisterUserUseCaseDep
) -> RegisterResponseSchema:
    """Register a new user"""
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
    use_case: ActivateUserUseCaseDep,
    credentials: HTTPEmailPasswordBasicCredentialsDep,
) -> ActivateResponseSchema:
    """Activate user account"""
    dto = ActivateUserRequest(
        email=Email(credentials.email),
        password=credentials.password,
        code=VerificationCode(request.code),
    )
    result = await use_case.execute(dto)

    return ActivateResponseSchema(
        user_id=result.user_id.value,
        email=result.email.value,
        is_active=result.is_active,
    )


@router.post(
    "/resend-code",
    status_code=status.HTTP_200_OK,
    summary="Resend verification code",
)
async def resend_code(
    use_case: ResendCodeUseCaseDep,
    credentials: HTTPEmailPasswordBasicCredentialsDep,
) -> ResendCodeResponseSchema:
    """Resend verification code"""
    dto = ResendCodeRequest(
        Email(credentials.email),
        credentials.password,
    )
    result = await use_case.execute(dto)

    return ResendCodeResponseSchema(
        email=result.email.value,
        message=result.message,
    )
