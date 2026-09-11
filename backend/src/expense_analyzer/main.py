from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

origins = [
    "http://localhost:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Allows specific domains
    allow_credentials=True,          # Allows cookies and auth headers
    allow_methods=["*"],             # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],             # Allows all request headers
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