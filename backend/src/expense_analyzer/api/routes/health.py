from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
def health_check() -> dict[str, str]:
    return{
        "status": "healthy",
    }
from fastapi import APIRouter

from expense_analyzer.core.config import get_settings


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

settings = get_settings()


@router.get("")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version,
    }