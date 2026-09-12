from datetime import datetime, timezone
from uuid import uuid4

import pytest

from expense_analyzer.domain.entities.user import User
from expense_analyzer.repositories.user_repository import (
    UserRepository,
)
from expense_analyzer.security.password import hash_password


@pytest.fixture
def user_repository():
    return UserRepository()


@pytest.fixture
def test_user():
    now = datetime.now(timezone.utc)

    return User(
        id=uuid4(),
        email=f"test-{uuid4()}@example.com",
        password_hash=hash_password("TestPassword123!"),
        is_active=True,
        created_at=now,
        updated_at=now,
    )


def test_create_user(user_repository, test_user):
    created_user = user_repository.create_user(test_user)

    assert created_user.id == test_user.id
    assert created_user.email == test_user.email
    assert created_user.password_hash == test_user.password_hash
    assert created_user.is_active is True


def test_find_user_by_email(user_repository, test_user):
    user_repository.create_user(test_user)

    found_user = user_repository.find_by_email(
        test_user.email
    )

    assert found_user is not None
    assert found_user.id == test_user.id
    assert found_user.email == test_user.email


def test_find_user_by_non_existing_email(user_repository):
    email = f"missing-{uuid4()}@example.com"

    found_user = user_repository.find_by_email(email)

    assert found_user is None


def test_find_user_by_id(user_repository, test_user):
    user_repository.create_user(test_user)

    found_user = user_repository.find_by_id(test_user.id)

    assert found_user is not None
    assert found_user.id == test_user.id


def test_find_user_by_non_existing_id(user_repository):
    user_id = uuid4()

    found_user = user_repository.find_by_id(user_id)

    assert found_user is None


def test_email_exists(user_repository, test_user):
    user_repository.create_user(test_user)

    assert user_repository.email_exists(
        test_user.email
    ) is True


def test_email_does_not_exist(user_repository):
    email = f"missing-{uuid4()}@example.com"

    assert user_repository.email_exists(email) is False
