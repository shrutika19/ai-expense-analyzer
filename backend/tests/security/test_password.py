from expense_analyzer.security.password import (
    hash_password,
    verify_password,
)


def test_password_is_hashed():
    password = "StrongPassword123!"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password.startswith("$argon2")


def test_correct_password_is_verified():
    password = "StrongPassword123!"

    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_wrong_password_is_rejected():
    password = "StrongPassword123!"

    hashed_password = hash_password(password)

    assert verify_password("WrongPassword123!", hashed_password) is False


def test_same_password_generates_different_hashes():
    password = "StrongPassword123!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash


def test_hash_can_be_verified_after_multiple_hashes():
    password = "StrongPassword123!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert verify_password(password, first_hash) is True
    assert verify_password(password, second_hash) is True