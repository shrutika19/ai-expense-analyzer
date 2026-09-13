from uuid import UUID

from fastapi import APIRouter, Depends, status

from expense_analyzer.api.v1.dependencies import (
    get_current_user,
    get_expense_service,
)
from expense_analyzer.api.v1.schemas.expense import (
    ExpenseCreateRequest,
    ExpenseResponse,
)
from expense_analyzer.domain.entities.user import User
from expense_analyzer.services.expense_service import ExpenseService


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)


@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    request: ExpenseCreateRequest,
    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> ExpenseResponse:

    expense = service.create_expense(
        request=request,
        user_id=current_user.id,
    )

    return ExpenseResponse.model_validate(expense)


@router.get(
    "",
    response_model=list[ExpenseResponse],
)
def get_expenses(
    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> list[ExpenseResponse]:

    expenses = service.get_expenses(
        user_id=current_user.id,
    )

    return [
        ExpenseResponse.model_validate(expense)
        for expense in expenses
    ]


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
def get_expense(
    expense_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> ExpenseResponse:
    expense = service.get_expense(expense_id, user_id=current_user.id)

    return ExpenseResponse.model_validate(expense)