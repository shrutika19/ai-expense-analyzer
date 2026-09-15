import pandas as pd
import pytest

from expense_analyzer.domain.enums.expense_category import (
    ExpenseCategory,
)
from expense_analyzer.ml.features.feature_pipeline import (
    FeaturePipeline,
)
from expense_analyzer.ml.training.trainer import (
    CategoryModelTrainer,
    TrainedModel,
)


def create_training_data():
    categories = list(ExpenseCategory)

    if len(categories) < 2:
        raise ValueError(
            "Tests require at least two expense categories."
        )

    category_1 = categories[0].value
    category_2 = categories[1].value

    X_train = pd.DataFrame(
        {
            "description": [
                "expense one",
                "expense two",
                "expense three",
                "expense four",
                "expense five",
                "expense six",
            ],
            "amount": [
                100,
                200,
                150,
                300,
                250,
                400,
            ],
        }
    )

    y_train = pd.Series(
        [
            category_1,
            category_1,
            category_1,
            category_2,
            category_2,
            category_2,
        ],
        name="category",
    )

    return X_train, y_train


def create_three_class_training_data():
    categories = list(ExpenseCategory)

    if len(categories) < 3:
        pytest.skip(
            "At least three expense categories are required."
        )

    category_1 = categories[0].value
    category_2 = categories[1].value
    category_3 = categories[2].value

    X_train = pd.DataFrame(
        {
            "description": [
                "expense one",
                "expense two",
                "expense three",
                "expense four",
                "expense five",
                "expense six",
                "expense seven",
                "expense eight",
                "expense nine",
            ],
            "amount": [
                100,
                150,
                200,
                250,
                300,
                350,
                400,
                450,
                500,
            ],
        }
    )

    y_train = pd.Series(
        [
            category_1,
            category_1,
            category_1,
            category_2,
            category_2,
            category_2,
            category_3,
            category_3,
            category_3,
        ],
        name="category",
    )

    return X_train, y_train


def create_test_data():
    categories = list(ExpenseCategory)

    category_1 = categories[0].value
    category_2 = categories[1].value

    X_test = pd.DataFrame(
        {
            "description": [
                "new expense one",
                "new expense two",
            ],
            "amount": [
                175,
                325,
            ],
        }
    )

    y_test = pd.Series(
        [
            category_1,
            category_2,
        ],
        name="category",
    )

    return X_test, y_test


def test_empty_training_dataset():
    trainer = CategoryModelTrainer()

    X_train = pd.DataFrame(
        columns=["description", "amount"]
    )

    y_train = pd.Series(
        dtype=str,
        name="category",
    )

    with pytest.raises(
        ValueError,
        match="Training data cannot be empty",
    ):
        trainer.train(
            X_train,
            y_train,
        )


def test_missing_target():
    X_train, y_train = create_training_data()

    y_train.iloc[0] = None

    trainer = CategoryModelTrainer()

    with pytest.raises(
        ValueError,
        match="Training target cannot contain missing values",
    ):
        trainer.train(
            X_train,
            y_train,
        )


def test_one_class_dataset():
    X_train, y_train = create_training_data()

    y_train = pd.Series(
        [y_train.iloc[0]] * len(y_train),
        name="category",
    )

    trainer = CategoryModelTrainer()

    with pytest.raises(
        ValueError,
        match="at least 2 categories",
    ):
        trainer.train(
            X_train,
            y_train,
        )


def test_valid_multi_class_dataset():
    X_train, y_train = create_training_data()

    assert y_train.nunique() >= 2

    trainer = CategoryModelTrainer()

    trained_model = trainer.train(
        X_train,
        y_train,
    )

    assert isinstance(
        trained_model,
        TrainedModel,
    )


def test_successful_training():
    X_train, y_train = create_training_data()

    trainer = CategoryModelTrainer()

    trained_model = trainer.train(
        X_train,
        y_train,
    )

    assert trained_model.classifier is not None
    assert trained_model.feature_pipeline is not None


def test_expected_number_of_classes():
    X_train, y_train = create_three_class_training_data()

    trainer = CategoryModelTrainer()

    trained_model = trainer.train(
        X_train,
        y_train,
    )

    assert len(
        trained_model.classifier.classes_
    ) == y_train.nunique()


def test_predict_works():
    X_train, y_train = create_training_data()
    X_test, _ = create_test_data()

    trainer = CategoryModelTrainer()

    trained_model = trainer.train(
        X_train,
        y_train,
    )

    feature_matrix = (
        trained_model.feature_pipeline.transform(
            X_test
        )
    )

    predictions = (
        trained_model.classifier.predict(
            feature_matrix
        )
    )

    assert len(predictions) == len(X_test)

    for prediction in predictions:
        assert prediction in (
            trained_model.classifier.classes_
        )


def test_predict_proba_works():
    X_train, y_train = create_training_data()
    X_test, _ = create_test_data()

    trainer = CategoryModelTrainer()

    trained_model = trainer.train(
        X_train,
        y_train,
    )

    feature_matrix = (
        trained_model.feature_pipeline.transform(
            X_test
        )
    )

    probabilities = (
        trained_model.classifier.predict_proba(
            feature_matrix
        )
    )

    assert probabilities.shape == (
        len(X_test),
        y_train.nunique(),
    )


def test_probabilities_are_valid():
    X_train, y_train = create_training_data()
    X_test, _ = create_test_data()

    trainer = CategoryModelTrainer()

    trained_model = trainer.train(
        X_train,
        y_train,
    )

    feature_matrix = (
        trained_model.feature_pipeline.transform(
            X_test
        )
    )

    probabilities = (
        trained_model.classifier.predict_proba(
            feature_matrix
        )
    )

    assert (probabilities >= 0).all()
    assert (probabilities <= 1).all()

    row_sums = probabilities.sum(axis=1)

    assert all(
        pytest.approx(total, abs=1e-9) == 1.0
        for total in row_sums
    )


def test_training_is_reproducible():
    X_train, y_train = create_training_data()

    trainer_1 = CategoryModelTrainer()
    trainer_2 = CategoryModelTrainer()

    model_1 = trainer_1.train(
        X_train,
        y_train,
    )

    model_2 = trainer_2.train(
        X_train,
        y_train,
    )

    features_1 = (
        model_1.feature_pipeline.transform(
            X_train
        )
    )

    features_2 = (
        model_2.feature_pipeline.transform(
            X_train
        )
    )

    probabilities_1 = (
        model_1.classifier.predict_proba(
            features_1
        )
    )

    probabilities_2 = (
        model_2.classifier.predict_proba(
            features_2
        )
    )

    assert model_1.classifier.classes_.tolist() == (
        model_2.classifier.classes_.tolist()
    )

    assert probabilities_1.tolist() == (
        probabilities_2.tolist()
    )



def test_feature_pipeline_is_fitted_only_on_training_data():
    X_train, y_train = create_training_data()

    X_test = pd.DataFrame(
        {
            "description": [
                "completely unique unseen vocabulary",
            ],
            "amount": [
                9999,
            ],
        }
    )

    trainer = CategoryModelTrainer()

    trained_model = trainer.train(
        X_train,
        y_train,
    )

    vocabulary_before = (
        trained_model
        .feature_pipeline
        .get_metadata()
        .tfidf
        .vocabulary
    )

    trained_model.feature_pipeline.transform(
        X_test
    )

    vocabulary_after = (
        trained_model
        .feature_pipeline
        .get_metadata()
        .tfidf
        .vocabulary
    )

    assert vocabulary_before == vocabulary_after