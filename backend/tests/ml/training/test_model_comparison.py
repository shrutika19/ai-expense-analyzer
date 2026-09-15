from expense_analyzer.ml.training.model_comparison import (
    ModelComparison,
)


def test_model_comparison_contains_both_models():
    comparison = ModelComparison()

    assert (
        comparison.model_a_name
        == "baseline_tfidf_logistic_model_a"
    )

    assert (
        comparison.model_b_name
        == "baseline_tfidf_logistic_model_b"
    )


def test_model_a_uses_only_description():
    comparison = ModelComparison()

    assert (
        comparison.model_a_features
        == "TF-IDF(description)"
    )

    assert comparison.model_a_amount_included is False


def test_model_b_uses_description_and_amount():
    comparison = ModelComparison()

    assert (
        comparison.model_b_features
        == "TF-IDF(description) + amount"
    )

    assert comparison.model_b_amount_included is True


def test_comparison_is_immutable():
    comparison = ModelComparison()

    try:
        comparison.model_a_name = "another_model"
        assert False, "ModelComparison should be immutable"
    except AttributeError:
        pass