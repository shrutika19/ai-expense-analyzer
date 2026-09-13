import pytest

from expense_analyzer.security.password_policy import (
    validate_password,
)


def test_valid_password() -> None:
    validate_password("Admin@123")


def test_password_too_short() -> None:
    with pytest.raises(ValueError):
        validate_password("Ab@123")


def test_password_too_long() -> None:
    password = "A" * 127 + "a1@"

    with pytest.raises(ValueError):
        validate_password(password)


def test_password_requires_uppercase() -> None:
    with pytest.raises(ValueError):
        validate_password("admin@123")


def test_password_requires_lowercase() -> None:
    with pytest.raises(ValueError):
        validate_password("ADMIN@123")


def test_password_requires_digit() -> None:
    with pytest.raises(ValueError):
        validate_password("Admin@abc")


def test_password_requires_special_character() -> None:
    with pytest.raises(ValueError):
        validate_password("Admin123")