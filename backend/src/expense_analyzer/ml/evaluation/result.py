from dataclasses import dataclass


@dataclass(frozen=True)
class PerCategoryMetrics:
    """Evaluation metrics for a single expense category."""

    category: str
    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class EvaluatedPrediction:
    description: str
    actual_category: str
    predicted_category: str
    confidence: float
    correct: bool


@dataclass(frozen=True)
class ConfidenceSummary:
    correct_mean: float | None
    incorrect_mean: float | None
    bands: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class ConfusionPair:
    actual_category: str
    predicted_category: str
    count: int


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

    evaluated_predictions: tuple[EvaluatedPrediction, ...] = ()
    confidence_summary: ConfidenceSummary | None = None
    top_confusions: tuple[ConfusionPair, ...] = ()