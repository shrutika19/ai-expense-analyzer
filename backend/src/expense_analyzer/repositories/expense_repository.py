from uuid import UUID

from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.infrastructure.database.connection import (
    get_connection,
)

from expense_analyzer.domain.enums.expense_category import (
    ExpenseCategory,
)


class ExpenseRepository:

    def save(self, expense: Expense) -> Expense:
        query = """
            INSERT INTO expenses (
                id,
                amount,
                description,
                category,
                expense_date
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        expense.id,
                        expense.amount,
                        expense.description,
                        expense.category.value,
                        expense.expense_date,
                    ),
                )

        return expense

    def find_all(self) -> list[Expense]:
        query = """
            SELECT
                id,
                amount,
                description,
                category,
                expense_date
            FROM expenses
            ORDER BY expense_date DESC, created_at DESC
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)

                rows = cursor.fetchall()

        return [
            self._map_row_to_expense(row)
            for row in rows
        ]

    @staticmethod
    def _map_row_to_expense(
        row: tuple,
    ) -> Expense:
        return Expense(
            id=UUID(str(row[0])),
            amount=row[1],
            description=row[2],
            category=ExpenseCategory(row[3]),
            expense_date=row[4],
        )