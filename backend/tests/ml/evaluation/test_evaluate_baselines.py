from unittest.mock import Mock, patch

import pandas as pd

from expense_analyzer.ml.evaluation.evaluate_baselines import (
    find_biggest_confusions,
    evaluate_baselines,
    print_biggest_confusions,
)


def test_find_biggest_confusions():
    """Returns the largest incorrect prediction pairs."""

    y_true = [
        "Food",
        "Food",
        "Food",
        "Transport",
        "Transport",
        "Travel",
        "Travel",
    ]

    y_pred = [
        "Food",
        "Transport",
        "Transport",
        "Travel",
        "Travel",
        "Travel",
        "Food",
    ]

    confusions = find_biggest_confusions(
        y_true=y_true,
        y_pred=y_pred,
        top_n=3,
    )

    assert len(confusions) == 3

    # Food -> Transport occurs twice.
    assert (
        "Food",
        "Transport",
        2,
    ) in confusions

    # Transport -> Travel occurs twice.
    assert (
        "Transport",
        "Travel",
        2,
    ) in confusions

    # Travel -> Food occurs once.
    assert (
        "Travel",
        "Food",
        1,
    ) in confusions


def test_find_biggest_confusions_excludes_correct_predictions():
    """Correct predictions must not appear as confusion pairs."""

    y_true = [
        "Food",
        "Transport",
        "Travel",
    ]

    y_pred = [
        "Food",
        "Transport",
        "Travel",
    ]

    confusions = find_biggest_confusions(
        y_true=y_true,
        y_pred=y_pred,
        top_n=5,
    )

    assert confusions == []


def test_print_biggest_confusions(
    capsys,
):
    """Prints the biggest confusion pairs."""

    y_true = [
        "Food",
        "Food",
        "Transport",
    ]

    y_pred = [
        "Transport",
        "Transport",
        "Transport",
    ]

    print_biggest_confusions(
        model_name="Model A",
        y_true=y_true,
        y_pred=y_pred,
        top_n=5,
    )

    output = capsys.readouterr().out

    assert (
        "Model A - Biggest Confusion Pairs"
        in output
    )

    assert (
        "Food -> Transport: 2 prediction(s)"
        in output
    )


@patch(
    "expense_analyzer.ml.evaluation.evaluate_baselines."
    "ModelEvaluator"
)
@patch(
    "expense_analyzer.ml.evaluation.evaluate_baselines."
    "DatasetPreparationPipeline"
)
def test_evaluate_baselines(
    mock_dataset_pipeline,
    mock_model_evaluator,
    capsys,
):
    """
    Verifies that evaluate_baselines uses the test
    labels only for evaluation and evaluates both models.
    """

    X_train = pd.DataFrame(
        {
            "description": [
                "grocery store",
                "bus ticket",
                "movie ticket",
                "rent payment",
            ],
            "amount": [
                100.0,
                50.0,
                200.0,
                1000.0,
            ],
        }
    )

    X_test = pd.DataFrame(
        {
            "description": [
                "restaurant",
                "taxi",
                "cinema",
            ],
            "amount": [
                300.0,
                150.0,
                250.0,
            ],
        }
    )

    y_train = pd.Series(
        [
            "Food",
            "Transport",
            "Entertainment",
            "Rent",
        ]
    )

    y_test = pd.Series(
        [
            "Food",
            "Transport",
            "Entertainment",
        ]
    )

    mock_dataset = Mock()

    mock_dataset.X_train = X_train
    mock_dataset.X_test = X_test
    mock_dataset.y_train = y_train
    mock_dataset.y_test = y_test

    mock_dataset_pipeline.return_value.prepare.return_value = (
        mock_dataset
    )

    model_a_predictions = Mock()
    model_a_predictions.predictions = [
        "Food",
        "Transport",
        "Entertainment",
    ]

    model_b_predictions = Mock()
    model_b_predictions.predictions = [
        "Food",
        "Transport",
        "Entertainment",
    ]

    mock_model_evaluator.return_value.evaluate.return_value = {
        "model_a": model_a_predictions,
        "model_b": model_b_predictions,
    }

    evaluate_baselines()

    # Verify dataset preparation was called.
    mock_dataset_pipeline.return_value.prepare.assert_called_once()

    # Verify both models received the correct train/test data.
    mock_model_evaluator.return_value.evaluate.assert_called_once_with(
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
    )

    output = capsys.readouterr().out

    assert "PHASE 6 - BASELINE MODEL EVALUATION" in output

    assert (
        "MODEL A - TF-IDF + Logistic Regression"
        in output
    )

    assert (
        "MODEL B - TF-IDF + Amount + Logistic Regression"
        in output
    )

    assert "EVALUATION COMPLETE" in output