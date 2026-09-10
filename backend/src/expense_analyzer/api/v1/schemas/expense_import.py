from pydantic import BaseModel, Field


class ExpenseImportError(BaseModel):
    row_number: int = Field(ge=1)
    reason: str


class ExpenseImportSkippedRow(BaseModel):
    row_number: int = Field(ge=1)
    reason: str


class ExpenseImportResponse(BaseModel):
    imported_count: int
    failed_count: int
    duplicate_count: int = 0
    message: str
    errors: list[ExpenseImportError] = Field(default_factory=list)
    skipped_rows: list[ExpenseImportSkippedRow] = Field(
        default_factory=list
    )