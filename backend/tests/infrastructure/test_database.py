from expense_analyzer.infrastructure.database.connection import (
    get_connection,
)
from expense_analyzer.core.config import get_settings



def test_database_connection() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

            result = cursor.fetchone()

    assert result == (1,)



def test_uses_test_database() -> None:
    settings = get_settings()

    assert settings.environment == "test"
    assert settings.database_name == "expense_analyzer_test"