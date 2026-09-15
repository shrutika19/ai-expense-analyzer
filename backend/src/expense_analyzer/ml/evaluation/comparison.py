from dataclasses import dataclass

from expense_analyzer.ml.evaluation.result import (
    ModelEvaluationResult,
)


@dataclass(frozen=True)
class ModelComparison:
    """Describes and compares the two baseline models."""

    model_a_name: str = (
        "baseline_tfidf_logistic_model_a"
    )

    model_b_name: str = (
        "baseline_tfidf_logistic_model_b"
    )

    model_a_features: str = (
        "TF-IDF(description)"
    )

    model_b_features: str = (
        "TF-IDF(description) + amount"
    )

    model_a_amount_included: bool = False

    model_b_amount_included: bool = True

    model_a_metrics: ModelEvaluationResult | None = None

    model_b_metrics: ModelEvaluationResult | None = None