import pandas as pd

from expense_analyzer.infrastructure.database.connection import get_connection


class DatasetLoader:
    """Loads categorized expense records from PostgreSQL."""

    def load(self) -> pd.DataFrame:
        query = """
            SELECT
                description,
                amount,
                category,
                expense_date
            FROM expenses
            ORDER BY created_at;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [column.name for column in cursor.description]

        return pd.DataFrame(rows, columns=columns)