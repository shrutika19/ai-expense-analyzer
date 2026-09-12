from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from expense_analyzer.api.exception_handlers import (
    expense_not_found_handler,
    inactive_user_handler,
    invalid_credentials_handler,
    invalid_token_handler,
    unsupported_file_type_handler,
    user_already_exists_handler,
    user_not_found_handler,
)
from expense_analyzer.api.routes.health import router as health_router
from expense_analyzer.api.v1.router import router as v1_router
from expense_analyzer.core.config import get_settings
from expense_analyzer.exceptions.api import (
    ExpenseNotFoundException,
)
from expense_analyzer.exceptions.auth import (
    InactiveUserException,
    InvalidCredentialsException,
    InvalidTokenException,
    UserAlreadyExistsException,
    UserNotFoundException,
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


origins = [
    "http://localhost:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health_router)
app.include_router(v1_router)


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------

app.add_exception_handler(
    ExpenseNotFoundException,
    expense_not_found_handler,
)

app.add_exception_handler(
    UnsupportedFileTypeException,
    unsupported_file_type_handler,
)

app.add_exception_handler(
    UserAlreadyExistsException,
    user_already_exists_handler,
)

app.add_exception_handler(
    InvalidCredentialsException,
    invalid_credentials_handler,
)

app.add_exception_handler(
    UserNotFoundException,
    user_not_found_handler,
)

app.add_exception_handler(
    InactiveUserException,
    inactive_user_handler,
)

app.add_exception_handler(
    InvalidTokenException,
    invalid_token_handler,
)