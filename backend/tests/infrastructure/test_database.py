from expense_analyzer.infrastructure.database.connection import (
    get_connection,
)


def test_database_connection() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

            result = cursor.fetchone()

    assert result == (1,)