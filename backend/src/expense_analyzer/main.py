from fastapi import FastAPI

from expense_analyzer.api.routes.health import router as health_router
from expense_analyzer.api.v1.router import router as v1_router
from expense_analyzer.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(health_router)
app.include_router(v1_router)