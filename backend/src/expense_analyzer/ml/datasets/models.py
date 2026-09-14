from pydantic import BaseModel, Field


class MissingValueStatistics(BaseModel):
    missing_count: int = Field(ge=0)
    missing_percentage: float = Field(ge=0.0, le=100.0)


class CategoryStatistics(BaseModel):
    record_count: int = Field(ge=0)
    percentage: float = Field(ge=0.0, le=100.0)


class AmountStatistics(BaseModel):
    min: float
    max: float
    mean: float


class DatasetStatistics(BaseModel):
    row_count: int = Field(ge=0)
    column_count: int = Field(ge=0)

    columns: dict[str, str]

    missing_values: dict[str, MissingValueStatistics]

    category_distribution: dict[str, CategoryStatistics]

    duplicate_count: int = Field(ge=0)

    amount_statistics: AmountStatistics