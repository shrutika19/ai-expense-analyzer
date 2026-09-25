from fastapi import APIRouter, Depends, status

from expense_analyzer.api.v1.dependencies import (
    get_current_user,
    get_inference_service,
    get_feedback_service,
)
from expense_analyzer.api.v1.schemas.ml import (
    CategoryPredictionRequest,
    CategoryPredictionResponse,
)
from expense_analyzer.domain.entities.user import User
from expense_analyzer.ml.inference.service import InferenceService
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
)
from expense_analyzer.ml.feedback.service import FeedbackService


router = APIRouter(
    prefix="/ml",
    tags=["Machine Learning"],
)


@router.post(
    "/predict-category",
    response_model=CategoryPredictionResponse,
    status_code=status.HTTP_200_OK,
)
def predict_category(
    request: CategoryPredictionRequest,
    current_user: User = Depends(get_current_user),
    service: InferenceService = Depends(get_inference_service),
) -> CategoryPredictionResponse:

    prediction = service.predict(
        CategoryPredictionInput(
            description=request.description,
            amount=request.amount,
        )
    )

    return CategoryPredictionResponse(
        predicted_category=prediction.predicted_category,
        confidence=prediction.confidence,
    )


@router.get("/feedback-dataset")
def get_feedback_dataset(
    current_user: User = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service),
) -> list[dict]:
    """Deduplicated, valid, user-confirmed examples for an offline retraining run."""
    return [record.__dict__ for record in service.dataset(current_user.id)]


@router.get("/feedback-performance")
def get_feedback_performance(
    current_user: User = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service),
) -> dict:
    """Model prediction versus final user-confirmed category."""
    return service.performance(current_user.id)


@router.get("/monitoring")
def get_monitoring(
    current_user: User = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service),
) -> dict:
    return service.monitoring(current_user.id)


@router.get("/feedback-diagnostics")
def get_feedback_diagnostics(
    current_user: User = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service),
) -> dict:
    return service.diagnose(current_user.id)
