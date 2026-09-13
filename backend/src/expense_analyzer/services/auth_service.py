from datetime import datetime, timezone
from uuid import uuid4

from expense_analyzer.domain.entities.user import User
from expense_analyzer.exceptions.auth import (
    InactiveUserException,
    InvalidCredentialsException,
    UserAlreadyExistsException,
)
from expense_analyzer.repositories.user_repository import UserRepository
from expense_analyzer.security.jwt import JWTService
from expense_analyzer.security.password import (
    hash_password,
    verify_password,
)


class AuthService:

    def __init__(
        self,
        user_repository: UserRepository,
        jwt_service: JWTService,
    ):
        self.user_repository = user_repository
        self.jwt_service = jwt_service

    def register_user(
        self,
        email: str,
        password: str,
    ) -> User:
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

        return self.user_repository.create_user(user)

    def login(
        self,
        email: str,
        password: str,
    ) -> dict:
        normalized_email = email.strip().lower()

        user = self.user_repository.find_by_email(
            normalized_email
        )

        if user is None:
            raise InvalidCredentialsException(
                "Invalid credentials"
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise InvalidCredentialsException(
                "Invalid credentials"
            )

        if not user.is_active:
            raise InactiveUserException(
                "User account is inactive"
            )

        access_token = self.jwt_service.create_access_token(
            user.id
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }