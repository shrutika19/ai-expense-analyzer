from expense_analyzer.ml.evaluation.comparison import (
    ModelComparison,
)


def test_baseline_comparison_records_features_without_metrics():
    comparison = ModelComparison()

    assert comparison.model_a_features == "TF-IDF(description)"
    assert comparison.model_b_features == (
        "TF-IDF(description) + amount"
    )
    assert comparison.model_a_amount_included is False
    assert comparison.model_b_amount_included is True
    assert comparison.model_a_metrics is None
    assert comparison.model_b_metrics is None