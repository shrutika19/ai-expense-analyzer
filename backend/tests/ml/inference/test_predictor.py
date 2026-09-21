from unittest.mock import Mock

import numpy as np

from expense_analyzer.ml.inference.predictor import (
    CategoryPredictor,
)
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
)


def test_predictor_returns_category_and_confidence() -> None:
    feature_pipeline = Mock()

    feature_pipeline.transform.return_value = np.array(
        [[1.0, 0.0, 25.0]]
    )

    classifier = Mock()

    classifier.predict.return_value = np.array(
        ["Food"]
    )

    classifier.predict_proba.return_value = np.array(
        [[0.90, 0.10]]
    )

    bundle = Mock(
        feature_pipeline=feature_pipeline,
        classifier=classifier,
    )

    predictor = CategoryPredictor()

    result = predictor.predict(
        bundle,
        CategoryPredictionInput(
            description="restaurant lunch",
            amount=25.0,
        ),
    )

    assert result.predicted_category == "Food"
    assert result.confidence == 0.90

    feature_pipeline.transform.assert_called_once()
    classifier.predict.assert_called_once()
    classifier.predict_proba.assert_called_once()


def test_predictor_only_transforms_features() -> None:
    feature_pipeline = Mock()

    feature_pipeline.transform.return_value = np.array(
        [[1.0, 0.0, 25.0]]
    )

    classifier = Mock()

    classifier.predict.return_value = np.array(
        ["Food"]
    )

    classifier.predict_proba.return_value = np.array(
        [[0.85, 0.15]]
    )

    bundle = Mock(
        feature_pipeline=feature_pipeline,
        classifier=classifier,
    )

    predictor = CategoryPredictor()

    predictor.predict(
        bundle,
        CategoryPredictionInput(
            description="restaurant lunch",
            amount=25.0,
        ),
    )

    feature_pipeline.fit.assert_not_called()
    feature_pipeline.fit_transform.assert_not_called()