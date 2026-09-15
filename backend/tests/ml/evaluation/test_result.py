from expense_analyzer.ml.evaluation.result import (
    ModelEvaluationResult,
    PerCategoryMetrics,
)


def test_per_category_metrics_stores_values():
    result = PerCategoryMetrics(
        category="Food",
        precision=0.90,
        recall=0.80,
        f1=0.85,
    )

    assert result.category == "Food"
    assert result.precision == 0.90
    assert result.recall == 0.80
    assert result.f1 == 0.85


def test_model_evaluation_result_stores_metrics():
    result = ModelEvaluationResult(
        model_name="Model A",
        accuracy=0.82,
        macro_precision=0.90,
        macro_recall=0.81,
        macro_f1=0.82,
        weighted_precision=0.88,
        weighted_recall=0.82,
        weighted_f1=0.81,
        per_category_metrics=(
            PerCategoryMetrics(
                category="Food",
                precision=0.90,
                recall=1.00,
                f1=0.95,
            ),
        ),
        confusion_matrix=(
            (5, 1),
            (0, 4),
        ),
        labels=(
            "Food",
            "Transport",
        ),
    )

    assert result.model_name == "Model A"
    assert result.accuracy == 0.82
    assert result.macro_f1 == 0.82
    assert result.weighted_f1 == 0.81
    assert len(result.per_category_metrics) == 1
    assert result.confusion_matrix == (
        (5, 1),
        (0, 4),
    )