"""Maps between User domain entity and UserModel database model."""

from app.domain import Email, Password, User, UserId
from app.infrastructure.database.models.user_model import UserModel


class UserMapper:
    """Maps between User domain entity and UserModel database model."""

    @staticmethod
    def to_entity(model: UserModel) -> User:
        """Convert database model to domain entity."""
        return User(
            id=UserId(model.id),
            email=Email(model.email),
            password=Password.from_hash(model.hashed_password),
            is_active=model.is_active,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        """Convert domain entity to database model."""
        return UserModel(
            id=entity.id.value,
            email=entity.email.value,
            hashed_password=entity.password.hashed_value,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )
