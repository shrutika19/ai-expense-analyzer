from pydantic import BaseModel


class ExpenseImportResponse(BaseModel):
    imported_count: int
    failed_count: int
    message: str