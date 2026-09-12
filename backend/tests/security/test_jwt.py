import jwt
import pytest

from expense_analyzer.core.config import get_settings
from expense_analyzer.exceptions.auth import InvalidTokenException
from expense_analyzer.security.jwt import JWTService


def test_create_access_token():
    service = JWTService()

    user_id = "550e8400-e29b-41d4-a716-446655440000"

    token = service.create_access_token(user_id)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token():
    service = JWTService()

    user_id = "550e8400-e29b-41d4-a716-446655440000"

    token = service.create_access_token(user_id)

    decoded_user_id = service.decode_access_token(token)

    assert str(decoded_user_id) == user_id


def test_token_contains_subject():
    service = JWTService()
    settings = get_settings()

    user_id = "550e8400-e29b-41d4-a716-446655440000"

    token = service.create_access_token(user_id)

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == user_id


def test_expired_token_is_rejected():
    service = JWTService()

    expired_token = jwt.encode(
        {
            "sub": "550e8400-e29b-41d4-a716-446655440000",
            "exp": 0,
        },
        get_settings().jwt_secret_key,
        algorithm=get_settings().jwt_algorithm,
    )

    with pytest.raises(InvalidTokenException):
        service.decode_access_token(expired_token)


def test_invalid_token_is_rejected():
    service = JWTService()

    with pytest.raises(InvalidTokenException):
        service.decode_access_token("this-is-not-a-valid-token")


def test_token_signed_with_wrong_secret_is_rejected():
    service = JWTService()

    wrong_secret_token = jwt.encode(
        {
            "sub": "550e8400-e29b-41d4-a716-446655440000",
        },
        "wrong-secret",
        algorithm="HS256",
    )

    with pytest.raises(InvalidTokenException):
        service.decode_access_token(wrong_secret_token)


def test_token_without_subject_is_rejected():
    service = JWTService()
    settings = get_settings()

    token = jwt.encode(
        {},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(InvalidTokenException):
        service.decode_access_token(token)