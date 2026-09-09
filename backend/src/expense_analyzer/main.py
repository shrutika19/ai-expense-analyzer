from fastapi import FastAPI

from expense_analyzer.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version,
    }