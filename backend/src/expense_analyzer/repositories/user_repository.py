from uuid import UUID

from expense_analyzer.domain.entities.user import User
from expense_analyzer.infrastructure.database.connection import (
    get_connection,
)


class UserRepository:

    def create_user(self, user: User) -> User:
        query = """
            INSERT INTO users (
                id,
                email,
                password_hash,
                is_active,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING
                id,
                email,
                password_hash,
                is_active,
                created_at,
                updated_at;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        user.id,
                        str(user.email),
                        user.password_hash,
                        user.is_active,
                        user.created_at,
                        user.updated_at,
                    ),
                )

                row = cursor.fetchone()

        return self._map_row_to_user(row)

    def find_by_email(self, email: str) -> User | None:
        query = """
            SELECT
                id,
                email,
                password_hash,
                is_active,
                created_at,
                updated_at
            FROM users
            WHERE email = %s;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (email,))
                row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row_to_user(row)

    def find_by_id(self, user_id: UUID) -> User | None:
        query = """
            SELECT
                id,
                email,
                password_hash,
                is_active,
                created_at,
                updated_at
            FROM users
            WHERE id = %s;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row_to_user(row)

    def email_exists(self, email: str) -> bool:
        query = """
            SELECT EXISTS (
                SELECT 1
                FROM users
                WHERE email = %s
            );
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (email,))
                result = cursor.fetchone()

        return bool(result[0])

    @staticmethod
    def _map_row_to_user(row: tuple) -> User:
        return User(
            id=row[0],
            email=row[1],
            password_hash=row[2],
            is_active=row[3],
            created_at=row[4],
            updated_at=row[5],
        )