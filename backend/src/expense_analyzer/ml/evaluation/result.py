from dataclasses import dataclass


@dataclass(frozen=True)
class PerCategoryMetrics:
    """Evaluation metrics for a single expense category."""

    category: str
    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class ModelEvaluationResult:
    """Complete evaluation result for a classification model."""

    model_name: str

    accuracy: float

    macro_precision: float
    macro_recall: float
    macro_f1: float

    weighted_precision: float
    weighted_recall: float
    weighted_f1: float

    per_category_metrics: tuple[
        PerCategoryMetrics,
        ...,
    ]

    confusion_matrix: tuple[
        tuple[int, ...],
        ...,
    ]

    labels: tuple[str, ...]