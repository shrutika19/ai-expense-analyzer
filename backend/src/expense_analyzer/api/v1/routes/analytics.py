from fastapi import APIRouter, Depends

from expense_analyzer.analytics.service import AnalyticsService
from expense_analyzer.api.v1.dependencies import (
    get_analytics_service,
)
from expense_analyzer.api.v1.schemas.analytics import (
    CategorySummaryResponse,
    ExpenseSummaryResponse,
    MonthlySummaryResponse,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/summary",
    response_model=ExpenseSummaryResponse,
)
def get_summary(
    service: AnalyticsService = Depends(get_analytics_service),
) -> ExpenseSummaryResponse:
    summary = service.get_summary()

    return ExpenseSummaryResponse.model_validate(summary)


@router.get(
    "/categories",
    response_model=list[CategorySummaryResponse],
)
def get_category_summary(
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[CategorySummaryResponse]:
    summaries = service.get_category_summary()

    return [
        CategorySummaryResponse.model_validate(summary)
        for summary in summaries
    ]


@router.get(
    "/monthly",
    response_model=list[MonthlySummaryResponse],
)
def get_monthly_summary(
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[MonthlySummaryResponse]:
    summaries = service.get_monthly_summary()

    return [
        MonthlySummaryResponse.model_validate(summary)
        for summary in summaries
    ]