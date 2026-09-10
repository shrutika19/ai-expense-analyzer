from fastapi import Request
from fastapi.responses import JSONResponse

from expense_analyzer.exceptions.api import (
    ExpenseNotFoundException,
)

from expense_analyzer.exceptions.expense_import import (
    UnsupportedFileTypeException,
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


def unsupported_file_type_handler(
    request: Request,
    exc: UnsupportedFileTypeException,
) -> JSONResponse:
    return JSONResponse(
        status_code=415,
        content={
            "error": {
                "code": "UNSUPPORTED_FILE_TYPE",
                "message": str(exc),
            }
        },
    )