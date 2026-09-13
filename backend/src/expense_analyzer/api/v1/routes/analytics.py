from fastapi import APIRouter, Depends

from expense_analyzer.analytics.service import AnalyticsService
from expense_analyzer.api.v1.dependencies import (
    get_analytics_service,
    get_current_user,
)
from expense_analyzer.api.v1.schemas.analytics import (
    CategorySummaryResponse,
    ExpenseSummaryResponse,
    MonthlySummaryResponse,
)
from expense_analyzer.domain.entities.user import User

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/summary",
    response_model=ExpenseSummaryResponse,
)
def get_summary(
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> ExpenseSummaryResponse:
    summary = service.get_summary(
        user_id=current_user.id,
    )

    return ExpenseSummaryResponse.model_validate(summary)


@router.get(
    "/categories",
    response_model=list[CategorySummaryResponse],
)
def get_category_summary(
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[CategorySummaryResponse]:
    summaries = service.get_category_summary(
        user_id=current_user.id,
    )

    return [
        CategorySummaryResponse.model_validate(summary)
        for summary in summaries
    ]


@router.get(
    "/monthly",
    response_model=list[MonthlySummaryResponse],
)
def get_monthly_summary(
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[MonthlySummaryResponse]:
    summaries = service.get_monthly_summary(
        user_id=current_user.id,
    )

    return [
        MonthlySummaryResponse.model_validate(summary)
        for summary in summaries
    ]