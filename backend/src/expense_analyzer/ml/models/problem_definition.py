from dataclasses import dataclass


@dataclass(frozen=True)
class CategoryPredictionProblem:
    name: str = "expense_category_prediction"
    task_type: str = "multiclass_classification"
    input_features: tuple[str, ...] = (
        "description",
        "amount",
    )
    target: str = "category"