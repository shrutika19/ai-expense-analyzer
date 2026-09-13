from datetime import datetime, timezone
from uuid import uuid4

from expense_analyzer.domain.entities.user import User
from expense_analyzer.exceptions.auth import (
    UserAlreadyExistsException,
)
from expense_analyzer.repositories.user_repository import UserRepository
from expense_analyzer.security.password import hash_password


class AuthService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register_user(self, email: str, password: str) -> User:

        normalized_email = email.strip().lower()

        if self.user_repository.email_exists(normalized_email):
            raise UserAlreadyExistsException(
                "User with this email already exists"
            )

        hashed_password = hash_password(password)

        now = datetime.now(timezone.utc)

        user = User(
            id=uuid4(),
            email=normalized_email,
            password_hash=hashed_password,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return user