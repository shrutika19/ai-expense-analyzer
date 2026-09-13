from fastapi import APIRouter, Depends, status

from expense_analyzer.api.v1.dependencies import get_auth_service
from expense_analyzer.api.v1.schemas.auth import (
    CurrentUserResponse,
    RegisterRequest,
)
from expense_analyzer.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.register_user(
        email=request.email,
        password=request.password,
    )