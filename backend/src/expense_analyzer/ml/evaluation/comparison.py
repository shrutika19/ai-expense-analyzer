from dataclasses import dataclass

from expense_analyzer.ml.evaluation.result import (
    ModelEvaluationResult,
)
from expense_analyzer.ml.training.experiment import (
    ExperimentMetadata,
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

    model_a_experiment: ExperimentMetadata | None = None

    model_b_experiment: ExperimentMetadata | None = None


def get_macro_f1_winner(
    comparison: ModelComparison,
) -> str | None:
    if (
        comparison.model_a_metrics is None
        or comparison.model_b_metrics is None
    ):
        return None

    model_a_f1 = comparison.model_a_metrics.macro_f1
    model_b_f1 = comparison.model_b_metrics.macro_f1

    if model_a_f1 == model_b_f1:
        return "Tie"

    return "Model A" if model_a_f1 > model_b_f1 else "Model B"