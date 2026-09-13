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
        self.save_many([expense])
        return expense

    def save_many(self, expenses: list[Expense]) -> list[Expense]:
        if not expenses:
            return []

        query = """
            INSERT INTO expenses (
                id,
                user_id,
                amount,
                description,
                category,
                expense_date
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                for expense in expenses:
                    cursor.execute(
                        query,
                        (
                            expense.id,
                            expense.user_id,
                            expense.amount,
                            expense.description,
                            expense.category.value,
                            expense.expense_date,
                        ),
                    )

        return expenses

    def find_all(self,user_id: UUID) -> list[Expense]:
        query = """
            SELECT
                id,
                user_id,
                amount,
                description,
                category,
                expense_date
            FROM expenses
            WHERE user_id = %s
            ORDER BY expense_date DESC, created_at DESC
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id,))

                rows = cursor.fetchall()

        return [
            self._map_row_to_expense(row)
            for row in rows
        ]

    def find_by_id(self, expense_id: UUID, user_id: UUID,) -> Expense | None:
        query = """
            SELECT
                id,
                user_id,
                amount,
                description,
                category,
                expense_date
            FROM expenses
            WHERE id = %s
                AND user_id = %s
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (expense_id,user_id))
                row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row_to_expense(row)

    @staticmethod
    def _map_row_to_expense(
        row: tuple,
    ) -> Expense:
        return Expense(
            id=UUID(str(row[0])),
            user_id=UUID(str(row[1])),
            amount=row[2],
            description=row[3],
            category=ExpenseCategory(row[4]),
            expense_date=row[5],
        )