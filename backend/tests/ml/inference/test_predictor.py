from unittest.mock import Mock

import numpy as np

from expense_analyzer.ml.inference.predictor import (
    MLPredictor,
)
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
)


def test_predictor_returns_highest_probability_category() -> None:
    feature_pipeline = Mock()

    feature_pipeline.transform.return_value = np.array(
        [[1.0, 0.0, 25.0]]
    )

    classifier = Mock()

    classifier.predict.return_value = np.array(
        ["Food"]
    )

    classifier.predict_proba.return_value = np.array(
        [[0.10, 0.90]]
    )

    model_bundle = Mock(
        feature_pipeline=feature_pipeline,
        classifier=classifier,
    )

    predictor = MLPredictor()

    prediction_input = CategoryPredictionInput(
        description="restaurant lunch",
        amount=25.0,
    )

    result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    assert result.predicted_category == "Food"
    assert result.confidence == 0.90



def test_predictor_uses_persisted_feature_pipeline() -> None:
    feature_pipeline = Mock()

    feature_pipeline.transform.return_value = np.array(
        [[1.0, 0.0, 25.0]]
    )

    classifier = Mock()

    classifier.predict.return_value = np.array(
        ["Food"]
    )

    classifier.predict_proba.return_value = np.array(
        [[0.15, 0.85]]
    )

    model_bundle = Mock(
        feature_pipeline=feature_pipeline,
        classifier=classifier,
    )

    predictor = MLPredictor()

    prediction_input = CategoryPredictionInput(
        description="restaurant lunch",
        amount=25.0,
    )

    predictor.predict(
        model_bundle,
        prediction_input,
    )

    feature_pipeline.transform.assert_called_once()

    feature_pipeline.fit.assert_not_called()
    feature_pipeline.fit_transform.assert_not_called()



def test_predictor_calls_predict_and_predict_proba() -> None:
    feature_pipeline = Mock()

    transformed_features = np.array(
        [[1.0, 0.0, 25.0]]
    )

    feature_pipeline.transform.return_value = (
        transformed_features
    )

    classifier = Mock()

    classifier.predict.return_value = np.array(
        ["Food"]
    )

    classifier.predict_proba.return_value = np.array(
        [[0.20, 0.80]]
    )

    model_bundle = Mock(
        feature_pipeline=feature_pipeline,
        classifier=classifier,
    )

    predictor = MLPredictor()

    prediction_input = CategoryPredictionInput(
        description="restaurant lunch",
        amount=25.0,
    )

    predictor.predict(
        model_bundle,
        prediction_input,
    )

    classifier.predict.assert_called_once_with(
        transformed_features
    )

    classifier.predict_proba.assert_called_once_with(
        transformed_features
    )



    def test_predictor_uses_highest_probability_as_confidence() -> None:
        feature_pipeline = Mock()

        feature_pipeline.transform.return_value = np.array(
            [[1.0, 0.0, 25.0]]
        )

        classifier = Mock()

        classifier.predict.return_value = np.array(
            ["Transport"]
        )

        classifier.predict_proba.return_value = np.array(
            [[0.05, 0.20, 0.75]]
        )

        model_bundle = Mock(
            feature_pipeline=feature_pipeline,
            classifier=classifier,
        )

        predictor = MLPredictor()

        prediction_input = CategoryPredictionInput(
            description="bus ticket",
            amount=25.0,
        )

        result = predictor.predict(
            model_bundle,
            prediction_input,
        )

        assert result.predicted_category == "Transport"
        assert result.confidence == 0.75