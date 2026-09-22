from fastapi import APIRouter, Depends, status

from expense_analyzer.api.v1.dependencies import (
    get_current_user,
    get_inference_service,
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