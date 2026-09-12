from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    password_hash: str
    is_active: bool = True
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )