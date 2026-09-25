from fastapi import APIRouter, HTTPException
from expense_analyzer.api.v1.dependencies import get_inference_service

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
def health_check() -> dict[str, str]:
    return{
        "status": "healthy",
    }


@router.get("/ready")
def readiness_check() -> dict:
    readiness = get_inference_service().readiness()
    if not readiness["ready"]:
        raise HTTPException(status_code=503, detail="ML model is not ready.")
    return {"status": "ready", "ml": readiness}
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


@router.get("/ready")
def configured_model_readiness() -> dict:
    readiness = get_inference_service().readiness()
    if not readiness["ready"]:
        raise HTTPException(status_code=503, detail="ML model is not ready.")
    return {"status": "ready", "ml": readiness}
