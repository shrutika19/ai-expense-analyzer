from fastapi import FastAPI

from expense_analyzer.api.routes.health import router as health_router
from expense_analyzer.api.v1.router import router as v1_router
from expense_analyzer.core.config import get_settings

from expense_analyzer.api.exception_handlers import (
    expense_not_found_handler,
    unsupported_file_type_handler,
)
from expense_analyzer.exceptions.api import (
    ExpenseNotFoundException,
)

from expense_analyzer.exceptions.expense_import import (
    UnsupportedFileTypeException,
)


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(health_router)
app.include_router(v1_router)

app.add_exception_handler(
    ExpenseNotFoundException,
    expense_not_found_handler,
)

app.add_exception_handler(
    UnsupportedFileTypeException,
    unsupported_file_type_handler,
)