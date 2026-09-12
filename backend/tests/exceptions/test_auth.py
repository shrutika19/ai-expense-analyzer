import pytest

from expense_analyzer.exceptions.auth import (
    AuthException,
    InactiveUserException,
    InvalidCredentialsException,
    InvalidTokenException,
    UserAlreadyExistsException,
    UserNotFoundException,
)


def test_auth_exception():
    with pytest.raises(AuthException):
        raise AuthException("Authentication error")


def test_user_already_exists_exception():
    with pytest.raises(UserAlreadyExistsException):
        raise UserAlreadyExistsException(
            "User already exists"
        )


def test_invalid_credentials_exception():
    with pytest.raises(InvalidCredentialsException):
        raise InvalidCredentialsException(
            "Invalid credentials"
        )


def test_user_not_found_exception():
    with pytest.raises(UserNotFoundException):
        raise UserNotFoundException(
            "User not found"
        )


def test_inactive_user_exception():
    with pytest.raises(InactiveUserException):
        raise InactiveUserException(
            "User is inactive"
        )


def test_invalid_token_exception():
    with pytest.raises(InvalidTokenException):
        raise InvalidTokenException(
            "Invalid token"
        )