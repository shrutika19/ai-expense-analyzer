from pydantic import BaseModel, Field


class CategoryPredictionInput(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=500,
    )
    amount: float = Field(
        gt=0,
    )


class CategoryPredictionOutput(BaseModel):
    predicted_category: str
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )