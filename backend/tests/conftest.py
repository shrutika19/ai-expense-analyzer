import os

os.environ["ENV_FILE"] = ".env.test"

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from expense_analyzer.domain.entities.user import User
from expense_analyzer.repositories.user_repository import UserRepository



from expense_analyzer.main import app


@pytest.fixture(scope="session", autouse=True)
def initialize_test_database() -> None:
    from expense_analyzer.infrastructure.database.init_db import (
        initialize_database,
    )

    initialize_database()


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def auth_headers(client: TestClient) -> dict[str, str]:
    email = f"testuser_{uuid4().hex}@example.com"
    password = "Test@12345"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201, (
        f"Registration failed: "
        f"{register_response.status_code} "
        f"{register_response.text}"
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200, (
        f"Login failed: "
        f"{login_response.status_code} "
        f"{login_response.text}"
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


@pytest.fixture(scope="session")
def test_user() -> User:
    user_repository = UserRepository()

    user = User(
        email=f"repository_test_{uuid4().hex}@example.com",
        password_hash="test_password_hash",
    )

    return user_repository.create_user(user)