from dataclasses import dataclass

from expense_analyzer.ml.evaluation.result import (
    ModelEvaluationResult,
)


@dataclass(frozen=True)
class AcceptanceCriteria:
    min_macro_f1: float | None = None
    minimum_recall_by_category: dict[str, float] | None = None


@dataclass(frozen=True)
class AcceptanceAssessment:
    decision: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class RegressionAssessment:
    decision: str
    macro_f1_delta: float


def assess_acceptance(
    result: ModelEvaluationResult,
    criteria: AcceptanceCriteria,
) -> AcceptanceAssessment:
    minimum_recalls = criteria.minimum_recall_by_category or {}

    if criteria.min_macro_f1 is None and not minimum_recalls:
        return AcceptanceAssessment(
            decision="not_configured",
            reasons=("Acceptance thresholds have not been configured.",),
        )

    reasons = []
    if (
        criteria.min_macro_f1 is not None
        and result.macro_f1 < criteria.min_macro_f1
    ):
        reasons.append(
            "Macro F1 is below the configured minimum."
        )

    recalls = {
        metric.category: metric.recall
        for metric in result.per_category_metrics
    }
    for category, minimum_recall in minimum_recalls.items():
        recall = recalls.get(category)
        if recall is None:
            reasons.append(
                f"Category '{category}' is missing from evaluation."
            )
        elif recall < minimum_recall:
            reasons.append(
                f"Recall for '{category}' is below the configured minimum."
            )

    return AcceptanceAssessment(
        decision="accepted" if not reasons else "rejected",
        reasons=tuple(reasons),
    )


def assess_regression(
    baseline: ModelEvaluationResult,
    candidate: ModelEvaluationResult,
    allowed_macro_f1_degradation: float,
) -> RegressionAssessment:
    if allowed_macro_f1_degradation < 0:
        raise ValueError("Allowed macro F1 degradation cannot be negative.")

    delta = candidate.macro_f1 - baseline.macro_f1
    if delta < -allowed_macro_f1_degradation:
        decision = "regression"
    elif delta > 0:
        decision = "improved"
    else:
        decision = "unchanged"

    return RegressionAssessment(
        decision=decision,
        macro_f1_delta=delta,
    )