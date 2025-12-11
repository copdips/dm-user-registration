"""Resend verification code use case."""

from app.application.dto.user_dto import ResendCodeRequest, ResendCodeResponse
from app.application.exceptions import InvalidCredentialsError, UserNotFoundError
from app.application.ports.code_store import CodeStore
from app.application.ports.event_publisher import EventPublisher
from app.application.ports.user_repository import UserRepository
from app.domain import UserNewVerificationCodeCreated, VerificationCode


class ResendCodeUseCase:
    """
    Use Case: Resend verification code.

    - Validates credentials (Basic Auth)
    - Generates new verification code
    - Stores code with TTL
    - Publishes UserRegistered event (to trigger email)
    """

    def __init__(
        self,
        user_repository: UserRepository,
        code_store: CodeStore,
        event_publisher: EventPublisher,
    ) -> None:
        self._user_repository: UserRepository = user_repository
        self._code_store: CodeStore = code_store
        self._event_publisher: EventPublisher = event_publisher

    async def execute(self, request: ResendCodeRequest) -> ResendCodeResponse:
        email = request.email
        password = request.password

        user = await self._user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundError(email.value)

        if not user.verify_password(password):
            raise InvalidCredentialsError(email.value)

        code = VerificationCode.generate()
        await self._code_store.save(email, code)

        event = UserNewVerificationCodeCreated(user_id=user.id, email=email)
        await self._event_publisher.publish(event)

        return ResendCodeResponse(
            email=email,
            message=f"New verification code has been sent to {email}.",
        )
