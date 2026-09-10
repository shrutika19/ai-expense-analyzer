class ExpenseNotFoundException(Exception):
    """Raised when an expense cannot be found."""

    def __init__(self, expense_id: str) -> None:
        self.expense_id = expense_id
        super().__init__(
            f"Expense with id '{expense_id}' was not found."
        )