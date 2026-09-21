from expense_analyzer.ml.evaluation.acceptance import (
    AcceptanceCriteria,
    assess_acceptance,
    assess_regression,
)
from expense_analyzer.ml.evaluation.result import (
    ModelEvaluationResult,
    PerCategoryMetrics,
)


def create_result(macro_f1: float, food_recall: float = 0.8):
    return ModelEvaluationResult(
        model_name="Model",
        accuracy=macro_f1,
        macro_precision=macro_f1,
        macro_recall=macro_f1,
        macro_f1=macro_f1,
        weighted_precision=macro_f1,
        weighted_recall=macro_f1,
        weighted_f1=macro_f1,
        per_category_metrics=(
            PerCategoryMetrics("Food", 0.8, food_recall, 0.8),
        ),
        confusion_matrix=((1,),),
        labels=("Food",),
    )


def test_unconfigured_acceptance_does_not_claim_readiness():
    assessment = assess_acceptance(
        create_result(0.8),
        AcceptanceCriteria(),
    )

    assert assessment.decision == "not_configured"


def test_acceptance_and_regression_are_evaluated_from_explicit_rules():
    assessment = assess_acceptance(
        create_result(0.8),
        AcceptanceCriteria(
            min_macro_f1=0.75,
            minimum_recall_by_category={"Food": 0.75},
        ),
    )
    regression = assess_regression(
        create_result(0.8),
        create_result(0.7),
        allowed_macro_f1_degradation=0.05,
    )

    assert assessment.decision == "accepted"
    assert regression.decision == "regression"