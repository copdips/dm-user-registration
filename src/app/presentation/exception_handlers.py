"""Exception handlers for FastAPI"""

from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse

from app.application.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    VerificationCodeExpiredError,
    VerificationCodeInvalidError,
)
from app.domain.exceptions import (
    InvalidEmailError,
    InvalidPasswordError,
    InvalidVerificationCodeError,
)

EXCEPTION_AND_STATUS_CODE = [
    (UserAlreadyExistsError, status.HTTP_409_CONFLICT),
    (UserNotFoundError, status.HTTP_404_NOT_FOUND),
    (InvalidCredentialsError, status.HTTP_401_UNAUTHORIZED),
    (VerificationCodeInvalidError, status.HTTP_400_BAD_REQUEST),
    (VerificationCodeExpiredError, status.HTTP_410_GONE),
    (InvalidEmailError, status.HTTP_400_BAD_REQUEST),
    (InvalidPasswordError, status.HTTP_401_UNAUTHORIZED),
    (InvalidVerificationCodeError, status.HTTP_400_BAD_REQUEST),
]


def register_exception_handler(app: FastAPI, exception: Any, status_code: int):
    @app.exception_handler(exception)
    async def exception_handler(
        _request: Request,
        ex: Exception,
    ):
        return JSONResponse(status_code=status_code, content={"message": str(ex)})


def register_unhandled_exception(app: FastAPI):
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        ex: Exception,
    ):
        exc_name = ex.__class__.__name__
        return await http_exception_handler(
            request,
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error {exc_name} occurred, ",
            ),
        )


def register_exception_handlers(app: FastAPI):
    register_unhandled_exception(app)
    for exception, status_code in EXCEPTION_AND_STATUS_CODE:
        register_exception_handler(app, exception, status_code)
