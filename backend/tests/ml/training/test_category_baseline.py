import pandas as pd
import pytest

from expense_analyzer.ml.training.category_baseline import (
    CategoryBaselineExperiment,
)


def create_training_data():
    X_train = pd.DataFrame(
        {
            "description": [
                "uber ride",
                "uber office",
                "taxi ride",
                "restaurant lunch",
                "restaurant dinner",
                "food restaurant",
                "amazon purchase",
                "amazon shopping",
                "shopping online",
            ],
            "amount": [
                350,
                500,
                400,
                250,
                450,
                300,
                1200,
                800,
                600,
            ],
        }
    )

    y_train = pd.Series(
        [
            "TRANSPORT",
            "TRANSPORT",
            "TRANSPORT",
            "FOOD",
            "FOOD",
            "FOOD",
            "SHOPPING",
            "SHOPPING",
            "SHOPPING",
        ]
    )

    return X_train, y_train


def create_test_data():
    return pd.DataFrame(
        {
            "description": [
                "uber ride",
                "restaurant lunch",
                "amazon purchase",
            ],
            "amount": [
                350,
                250,
                1200,
            ],
        }
    )


def test_logistic_regression_is_trained():
    X_train, y_train = create_training_data()

    experiment = CategoryBaselineExperiment()

    experiment.train(
        X_train,
        y_train,
    )

    assert experiment._is_trained is True
    assert hasattr(
        experiment.classifier,
        "classes_",
    )


def test_model_learns_expected_categories():
    X_train, y_train = create_training_data()

    experiment = CategoryBaselineExperiment()

    experiment.train(
        X_train,
        y_train,
    )

    assert set(
        experiment.classifier.classes_
    ) == {
        "TRANSPORT",
        "FOOD",
        "SHOPPING",
    }


def test_training_data_and_target_must_have_same_length():
    X_train, y_train = create_training_data()

    y_train = y_train.iloc[:-1]

    experiment = CategoryBaselineExperiment()

    with pytest.raises(
        ValueError,
        match="same number of rows",
    ):
        experiment.train(
            X_train,
            y_train,
        )


def test_empty_training_data_is_rejected():
    X_train, y_train = create_training_data()

    X_train = X_train.iloc[0:0]
    y_train = y_train.iloc[0:0]

    experiment = CategoryBaselineExperiment()

    with pytest.raises(
        ValueError,
        match="Training data cannot be empty",
    ):
        experiment.train(
            X_train,
            y_train,
        )


def test_missing_training_target_is_rejected():
    X_train, y_train = create_training_data()

    y_train.iloc[0] = None

    experiment = CategoryBaselineExperiment()

    with pytest.raises(
        ValueError,
        match="missing values",
    ):
        experiment.train(
            X_train,
            y_train,
        )


def test_prediction_requires_training():
    X_test = create_test_data()

    experiment = CategoryBaselineExperiment()

    with pytest.raises(
        RuntimeError,
        match="must be trained",
    ):
        experiment.predict(X_test)


def test_trained_model_can_predict():
    X_train, y_train = create_training_data()
    X_test = create_test_data()

    experiment = CategoryBaselineExperiment()

    experiment.train(
        X_train,
        y_train,
    )

    result = experiment.predict(X_test)

    assert len(
        result.predicted_categories
    ) == len(X_test)


def test_predictions_are_known_categories():
    X_train, y_train = create_training_data()
    X_test = create_test_data()

    experiment = CategoryBaselineExperiment()

    experiment.train(
        X_train,
        y_train,
    )

    result = experiment.predict(X_test)

    assert set(
        result.predicted_categories
    ).issubset(set(y_train))


def test_predict_proba_returns_probabilities():
    X_train, y_train = create_training_data()
    X_test = create_test_data()

    experiment = CategoryBaselineExperiment()

    experiment.train(
        X_train,
        y_train,
    )

    probabilities = experiment.predict_proba(
        X_test
    )

    assert len(probabilities) == len(X_test)

    assert all(
        len(row) == len(experiment.classifier.classes_)
        for row in probabilities
    )


def test_probabilities_are_between_zero_and_one():
    X_train, y_train = create_training_data()
    X_test = create_test_data()

    experiment = CategoryBaselineExperiment()

    experiment.train(
        X_train,
        y_train,
    )

    probabilities = experiment.predict_proba(
        X_test
    )

    for row in probabilities:
        assert all(
            0.0 <= probability <= 1.0
            for probability in row
        )


def test_probabilities_sum_to_one():
    X_train, y_train = create_training_data()
    X_test = create_test_data()

    experiment = CategoryBaselineExperiment()

    experiment.train(
        X_train,
        y_train,
    )

    probabilities = experiment.predict_proba(
        X_test
    )

    for row in probabilities:
        assert sum(row) == pytest.approx(1.0)


def test_predict_with_confidence_returns_category_and_confidence():
    X_train, y_train = create_training_data()
    X_test = create_test_data()

    experiment = CategoryBaselineExperiment()

    experiment.train(
        X_train,
        y_train,
    )

    results = experiment.predict_with_confidence(
        X_test
    )

    assert len(results) == len(X_test)

    for result in results:
        assert result.predicted_category in set(
            y_train
        )

        assert 0.0 <= result.confidence <= 1.0


def test_confidence_matches_predicted_class_probability():
    X_train, y_train = create_training_data()
    X_test = create_test_data()

    experiment = CategoryBaselineExperiment()

    experiment.train(
        X_train,
        y_train,
    )

    prediction_result = experiment.predict(
        X_test
    )

    predictions = prediction_result.predicted_categories

    probabilities = experiment.predict_proba(
        X_test
    )

    results = experiment.predict_with_confidence(
        X_test
    )

    classes = list(
        experiment.classifier.classes_
    )

    for prediction, probability_row, result in zip(
        predictions,
        probabilities,
        results,
    ):
        predicted_index = classes.index(
            prediction
        )

        expected_confidence = (
            probability_row[predicted_index]
        )

        assert result.confidence == pytest.approx(
            expected_confidence
        )

        assert result.predicted_category == prediction


def test_predict_proba_requires_training():
    X_test = create_test_data()

    experiment = CategoryBaselineExperiment()

    with pytest.raises(
        RuntimeError,
        match="must be trained",
    ):
        experiment.predict_proba(X_test)


def test_predict_with_confidence_requires_training():
    X_test = create_test_data()

    experiment = CategoryBaselineExperiment()

    with pytest.raises(
        RuntimeError,
        match="must be trained",
    ):
        experiment.predict_with_confidence(X_test)