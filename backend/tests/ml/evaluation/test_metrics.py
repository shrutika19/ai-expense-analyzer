from expense_analyzer.ml.evaluation.metrics import (
    calculate_accuracy,
    calculate_confusion_matrix,
    calculate_macro_f1,
    calculate_macro_precision,
    calculate_macro_recall,
    calculate_per_category_metrics,
    calculate_weighted_f1,
    calculate_weighted_precision,
    calculate_weighted_recall,
)


def test_accuracy():
    y_true = [
        "Food",
        "Food",
        "Transport",
        "Transport",
    ]

    y_pred = [
        "Food",
        "Food",
        "Transport",
        "Food",
    ]

    result = calculate_accuracy(
        y_true,
        y_pred,
    )

    assert result == 0.75


def test_macro_metrics_are_calculated():
    y_true = [
        "Food",
        "Food",
        "Transport",
        "Transport",
    ]

    y_pred = [
        "Food",
        "Food",
        "Transport",
        "Food",
    ]

    precision = calculate_macro_precision(
        y_true,
        y_pred,
    )

    recall = calculate_macro_recall(
        y_true,
        y_pred,
    )

    f1 = calculate_macro_f1(
        y_true,
        y_pred,
    )

    assert 0.0 <= precision <= 1.0
    assert 0.0 <= recall <= 1.0
    assert 0.0 <= f1 <= 1.0


def test_weighted_metrics_are_calculated():
    y_true = [
        "Food",
        "Food",
        "Transport",
        "Transport",
    ]

    y_pred = [
        "Food",
        "Food",
        "Transport",
        "Food",
    ]

    precision = calculate_weighted_precision(
        y_true,
        y_pred,
    )

    recall = calculate_weighted_recall(
        y_true,
        y_pred,
    )

    f1 = calculate_weighted_f1(
        y_true,
        y_pred,
    )

    assert 0.0 <= precision <= 1.0
    assert 0.0 <= recall <= 1.0
    assert 0.0 <= f1 <= 1.0


def test_per_category_metrics():
    y_true = [
        "Food",
        "Food",
        "Transport",
        "Transport",
    ]

    y_pred = [
        "Food",
        "Food",
        "Transport",
        "Food",
    ]

    result = calculate_per_category_metrics(
        y_true=y_true,
        y_pred=y_pred,
        labels=[
            "Food",
            "Transport",
        ],
    )

    assert len(result) == 2

    assert result[0].category == "Food"
    assert result[1].category == "Transport"

    for metric in result:
        assert 0.0 <= metric.precision <= 1.0
        assert 0.0 <= metric.recall <= 1.0
        assert 0.0 <= metric.f1 <= 1.0


def test_confusion_matrix():
    y_true = [
        "Food",
        "Food",
        "Transport",
        "Transport",
    ]

    y_pred = [
        "Food",
        "Food",
        "Transport",
        "Food",
    ]

    result = calculate_confusion_matrix(
        y_true=y_true,
        y_pred=y_pred,
        labels=[
            "Food",
            "Transport",
        ],
    )

    assert result == (
        (2, 0),
        (1, 1),
    )