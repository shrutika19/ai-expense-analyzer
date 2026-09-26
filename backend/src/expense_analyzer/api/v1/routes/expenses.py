from uuid import UUID

from fastapi import APIRouter, Depends, status

from expense_analyzer.api.v1.dependencies import (
    get_current_user,
    get_expense_service,
)
from expense_analyzer.api.v1.schemas.expense import (
    ExpenseCreateRequest,
    ExpenseResponse,
    ExpenseCategoryCorrectionRequest,
    ExpenseTableRequest,
    ExpenseTableResponse,
)
from expense_analyzer.domain.entities.user import User
from expense_analyzer.domain.enums.expense_category import ExpenseCategory
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


@router.post("/search", response_model=ExpenseTableResponse)
def search_expenses(request: ExpenseTableRequest, current_user: User = Depends(get_current_user),
                    service: ExpenseService = Depends(get_expense_service)) -> ExpenseTableResponse:
    items, total = service.search_expenses(current_user.id, **request.model_dump())
    return ExpenseTableResponse(items=[ExpenseResponse.model_validate(item) for item in items],
                                total_count=total, page=request.page, page_size=request.page_size)


@router.get("/categories", response_model=list[ExpenseCategory])
def get_categories(current_user: User = Depends(get_current_user)) -> list[ExpenseCategory]:
    return list(ExpenseCategory)


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


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: UUID, current_user: User = Depends(get_current_user),
                   service: ExpenseService = Depends(get_expense_service)) -> None:
    service.delete_expense(expense_id, current_user.id)


@router.patch("/{expense_id}/category", response_model=ExpenseResponse)
def correct_category(
    expense_id: UUID,
    request: ExpenseCategoryCorrectionRequest,
    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> ExpenseResponse:
    """Record a user-confirmed category while retaining the initial prediction."""
    return ExpenseResponse.model_validate(
        service.correct_category(expense_id, request.category, current_user.id)
    )
