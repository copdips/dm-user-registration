"""Email value object"""

import re
from dataclasses import dataclass

from app.domain.exceptions import InvalidEmailError

_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True, slots=True)
class Email:
    """
    Email value object.

    Validates format and normalizes to lowercase.
    """

    value: str

    def __post_init__(self) -> None:
        # Normalize to lowercase
        object.__setattr__(self, "value", self.value.strip().lower())

        if not self.value:
            msg = "Email cannot be empty"
            raise InvalidEmailError(msg)

        if not _EMAIL_PATTERN.match(self.value):
            msg = f"Invalid email format: {self.value}"
            raise InvalidEmailError(msg)
