import pytest

from expense_analyzer.ml.evaluation.analysis import (
    create_evaluated_predictions,
    find_top_confusions,
    summarize_confidence,
    validate_probabilities,
)


def test_confidence_analysis_records_correctness_and_bands():
    predictions = create_evaluated_predictions(
        descriptions=["lunch", "taxi"],
        y_true=["Food", "Transport"],
        y_pred=["Food", "Food"],
        probabilities=[[0.95, 0.05], [0.65, 0.35]],
    )

    summary = summarize_confidence(predictions)

    assert predictions[0].correct is True
    assert predictions[1].correct is False
    assert summary.correct_mean == 0.95
    assert summary.incorrect_mean == 0.65
    assert dict(summary.bands)["0.90-1.00"] == 1
    assert dict(summary.bands)["0.60-0.69"] == 1


def test_invalid_probability_rows_raise_errors():
    with pytest.raises(ValueError, match=r"in \[0, 1\]"):
        validate_probabilities([[1.1, -0.1]])

    with pytest.raises(ValueError, match="sum to 1"):
        validate_probabilities([[0.40, 0.50]])


def test_top_confusions_exclude_correct_predictions_and_sort_counts():
    pairs = find_top_confusions(
        confusion_matrix=((3, 2), (1, 4)),
        labels=("Food", "Transport"),
    )

    assert [(pair.actual_category, pair.predicted_category, pair.count) for pair in pairs] == [
        ("Food", "Transport", 2),
        ("Transport", "Food", 1),
    ]