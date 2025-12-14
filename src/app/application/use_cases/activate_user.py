"""Activate user use case."""

from app.application.dto.user_dto import ActivateUserRequest, ActivateUserResponse
from app.application.exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    VerificationCodeExpiredError,
    VerificationCodeInvalidError,
)
from app.application.ports.code_store import CodeStore
from app.application.ports.event_publisher import EventPublisher
from app.application.ports.unit_of_work import UnitOfWork


class ActivateUserUseCase:
    """
    Use Case: Activate a user account.

    - Validates basic auth
    - Validates verification code
    - Activates user account
    - Deletes verification code
    - Publishes UserActivated event
    """

    def __init__(
        self,
        uow: UnitOfWork,
        code_store: CodeStore,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow: UnitOfWork = uow
        self._code_store: CodeStore = code_store
        self._event_publisher: EventPublisher = event_publisher

    async def execute(self, request: ActivateUserRequest) -> ActivateUserResponse:
        email = request.email
        password = request.password

        async with self._uow:
            user = await self._uow.user_repository.get_by_email(email)
            if not user:
                raise UserNotFoundError(email.value)

            if not user.verify_password(password):
                raise InvalidCredentialsError(email.value)

            stored_code = await self._code_store.get(email)
            if stored_code is None:
                raise VerificationCodeExpiredError(email.value)

            if not stored_code.matches(request.code.value):
                raise VerificationCodeInvalidError(email.value)

            user.activate()
            await self._uow.user_repository.save(user)

            await self._code_store.delete(email)

            events = user.collect_events()
            await self._event_publisher.publish_all(events)

        return ActivateUserResponse(
            user_id=user.id,
            email=email,
            is_active=True,
        )
