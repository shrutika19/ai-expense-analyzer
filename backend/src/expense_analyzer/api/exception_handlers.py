from fastapi import Request
from fastapi.responses import JSONResponse

from expense_analyzer.exceptions.api import (
    ExpenseNotFoundException,
)


def expense_not_found_handler(
    request: Request,
    exc: ExpenseNotFoundException,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "EXPENSE_NOT_FOUND",
                "message": str(exc),
            }
        },
    )