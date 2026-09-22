from pydantic import BaseModel, Field


class CategoryPredictionRequest(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=500,
    )
    amount: float = Field(
        ge=0,
    )


class CategoryPredictionResponse(BaseModel):
    predicted_category: str
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )