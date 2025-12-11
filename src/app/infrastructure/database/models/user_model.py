"""User database model"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserModel(BaseModel):
    id: UUID
    email: str
    hashed_password: str
    is_active: bool
    created_at: datetime
