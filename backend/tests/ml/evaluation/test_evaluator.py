from unittest.mock import Mock

import numpy as np
import pytest


from expense_analyzer.ml.evaluation.evaluator import (
    ModelEvaluator,
)
from expense_analyzer.ml.training.trainer import (
    TrainedModel,
)


def test_evaluator_does_not_fit_test_data():
    feature_pipeline = Mock()

    feature_pipeline.transform.return_value = (
        np.array(
            [
                [1.0, 0.0],
                [0.0, 1.0],
            ]
        )
    )

    classifier = Mock()

    classifier.predict.return_value = np.array(
        [
            "Food",
            "Transport",
        ]
    )
    classifier.predict_proba.return_value = np.array(
        [
            [0.90, 0.10],
            [0.20, 0.80],
        ]
    )

    model = TrainedModel(
        classifier=classifier,
        feature_pipeline=feature_pipeline,
    )

    X_test = [
        {
            "description": "pizza",
        },
        {
            "description": "taxi",
        },
    ]

    y_test = [
        "Food",
        "Transport",
    ]

    evaluator = ModelEvaluator()

    result = evaluator.evaluate(
        model=model,
        model_name="Model A",
        X_test=X_test,
        y_test=y_test,
        labels=[
            "Food",
            "Transport",
        ],
    )

    feature_pipeline.transform.assert_called_once_with(
        X_test
    )

    feature_pipeline.fit.assert_not_called()

    feature_pipeline.fit_transform.assert_not_called()

    classifier.fit.assert_not_called()

    classifier.predict.assert_called_once()
    classifier.predict_proba.assert_called_once()

    assert result.accuracy == 1.0
    assert len(result.evaluated_predictions) == 2
    assert result.confidence_summary.correct_mean == pytest.approx(0.85)
    assert result.top_confusions == ()