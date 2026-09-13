from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import Mock

import pytest

from expense_analyzer.domain.entities.user import User
from expense_analyzer.exceptions.auth import (
    InactiveUserException,
    InvalidCredentialsException,
)
from expense_analyzer.services.auth_service import AuthService


def create_user(
    email: str = "pratik@email.com",
    password_hash: str = "hashed-password",
    is_active: bool = True,
) -> User:
    now = datetime.now(timezone.utc)

    return User(
        id=uuid4(),
        email=email,
        password_hash=password_hash,
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def user_repository():
    return Mock()


@pytest.fixture
def jwt_service():
    return Mock()


@pytest.fixture
def auth_service(user_repository, jwt_service):
    return AuthService(
        user_repository=user_repository,
        jwt_service=jwt_service,
    )


def test_login_success(
    auth_service,
    user_repository,
    jwt_service,
    monkeypatch,
):
    user = create_user()

    user_repository.find_by_email.return_value = user
    jwt_service.create_access_token.return_value = "test-jwt-token"

    monkeypatch.setattr(
        "expense_analyzer.services.auth_service.verify_password",
        lambda password, password_hash: True,
    )

    result = auth_service.login(
        email="PRATIK@email.com",
        password="admin@123",
    )

    assert result["access_token"] == "test-jwt-token"
    assert result["token_type"] == "bearer"

    user_repository.find_by_email.assert_called_once_with(
        "pratik@email.com"
    )

    jwt_service.create_access_token.assert_called_once_with(
        user.id
    )


def test_login_unknown_email(
    auth_service,
    user_repository,
):
    user_repository.find_by_email.return_value = None

    with pytest.raises(InvalidCredentialsException) as exc_info:
        auth_service.login(
            email="unknown@email.com",
            password="admin@123",
        )

    assert str(exc_info.value) == "Invalid credentials"


def test_login_wrong_password(
    auth_service,
    user_repository,
    monkeypatch,
):
    user = create_user()

    user_repository.find_by_email.return_value = user

    monkeypatch.setattr(
        "expense_analyzer.services.auth_service.verify_password",
        lambda password, password_hash: False,
    )

    with pytest.raises(InvalidCredentialsException) as exc_info:
        auth_service.login(
            email="pratik@email.com",
            password="wrong-password",
        )

    assert str(exc_info.value) == "Invalid credentials"


def test_login_inactive_user(
    auth_service,
    user_repository,
    monkeypatch,
):
    user = create_user(is_active=False)

    user_repository.find_by_email.return_value = user

    monkeypatch.setattr(
        "expense_analyzer.services.auth_service.verify_password",
        lambda password, password_hash: True,
    )

    with pytest.raises(InactiveUserException) as exc_info:
        auth_service.login(
            email="pratik@email.com",
            password="admin@123",
        )

    assert str(exc_info.value) == "User account is inactive"


def test_jwt_generated_after_successful_login(
    auth_service,
    user_repository,
    jwt_service,
    monkeypatch,
):
    user = create_user()

    user_repository.find_by_email.return_value = user
    jwt_service.create_access_token.return_value = "generated-token"

    monkeypatch.setattr(
        "expense_analyzer.services.auth_service.verify_password",
        lambda password, password_hash: True,
    )

    result = auth_service.login(
        email="pratik@email.com",
        password="admin@123",
    )

    assert result["access_token"] == "generated-token"

    jwt_service.create_access_token.assert_called_once_with(
        user.id
    )