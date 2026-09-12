from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from expense_analyzer.core.config import get_settings
from expense_analyzer.exceptions.auth import InvalidTokenException


settings = get_settings()


class JWTService:

    def create_access_token(self, user_id: UUID) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

        payload = {
            "sub": str(user_id),
            "exp": expires_at,
        }

        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    def decode_access_token(self, token: str) -> UUID:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )

            subject = payload.get("sub")

            if subject is None:
                raise InvalidTokenException("Token subject is missing")

            return UUID(subject)

        except (
            jwt.ExpiredSignatureError,
            jwt.InvalidTokenError,
            ValueError,
        ) as exc:
            raise InvalidTokenException(
                "Invalid or expired token"
            ) from exc