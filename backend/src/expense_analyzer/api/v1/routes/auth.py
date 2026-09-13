from fastapi import APIRouter, Depends, status

from expense_analyzer.api.v1.dependencies import get_auth_service
from expense_analyzer.api.v1.schemas.auth import (
    CurrentUserResponse,
    RegisterRequest,
    LoginRequest,
    TokenResponse
)
from expense_analyzer.services.auth_service import AuthService
from expense_analyzer.api.v1.dependencies import get_current_user
from expense_analyzer.domain.entities.user import User


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


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.login(
        email=request.email,
        password=request.password,
    )


@router.get(
    "/user",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
)
def get_user(
    current_user: User = Depends(get_current_user),
):
    return current_user