import pandas as pd

import expense_analyzer.ml.training.train_baseline as train_baseline
from expense_analyzer.domain.enums.expense_category import (
    ExpenseCategory,
)
from expense_analyzer.ml.training.train_baseline import (
    train_model_a,
    train_model_b,
)
from expense_analyzer.ml.training.experiment import (
    ExperimentMetadata,
)


def create_training_data():
    categories = list(ExpenseCategory)

    if len(categories) < 3:
        raise ValueError(
            "Tests require at least 3 supported expense categories."
        )

    category_1 = categories[0].value
    category_2 = categories[1].value
    category_3 = categories[2].value

    X_train = pd.DataFrame(
        {
            "description": [
                "uber ride",
                "taxi office",
                "bus ticket",
                "restaurant lunch",
                "restaurant dinner",
                "food delivery",
                "amazon purchase",
                "online shopping",
                "shopping order",
            ],
            "amount": [
                350,
                400,
                250,
                300,
                450,
                500,
                1200,
                800,
                600,
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


def test_model_a_uses_only_description():
    X_train, y_train = create_training_data()

    trained_model, benchmark = train_model_a(
        X_train,
        y_train,
    )

    assert trained_model.classifier is not None
    assert trained_model.feature_pipeline is not None

    assert benchmark["model"] == "Model A"
    assert benchmark["amount_included"] is False


def test_model_b_includes_amount():
    X_train, y_train = create_training_data()

    trained_model, benchmark = train_model_b(
        X_train,
        y_train,
    )

    assert trained_model.classifier is not None
    assert trained_model.feature_pipeline is not None

    assert benchmark["model"] == "Model B"
    assert benchmark["amount_included"] is True


def test_baseline_training_does_not_depend_on_model_storage():
    assert not hasattr(train_baseline, "ModelStorage")


def test_model_a_records_experiment_metadata():
    X_train, y_train = create_training_data()

    _, benchmark = train_model_a(
        X_train,
        y_train,
        test_row_count=2,
    )

    experiment = benchmark["experiment"]

    assert isinstance(experiment, ExperimentMetadata)
    assert experiment.experiment_name == (
        "baseline_tfidf_logistic_model_a"
    )
    assert experiment.model_type == "LogisticRegression"
    assert experiment.training_row_count == len(X_train)
    assert experiment.test_row_count == 2
    assert experiment.number_of_categories == y_train.nunique()
    assert experiment.feature_configuration["amount_included"] is False
    assert experiment.random_state == 42
    assert experiment.model_parameters["max_iterations"] == 1000


def test_model_a_records_training_sample_count():
    X_train, y_train = create_training_data()

    _, benchmark = train_model_a(
        X_train,
        y_train,
    )

    assert (
        benchmark["training_sample_count"]
        == len(X_train)
    )


def test_model_b_records_training_sample_count():
    X_train, y_train = create_training_data()

    _, benchmark = train_model_b(
        X_train,
        y_train,
    )

    assert (
        benchmark["training_sample_count"]
        == len(X_train)
    )


def test_model_a_records_number_of_categories():
    X_train, y_train = create_training_data()

    _, benchmark = train_model_a(
        X_train,
        y_train,
    )

    assert (
        benchmark["number_of_categories"]
        == y_train.nunique()
    )


def test_model_b_records_number_of_categories():
    X_train, y_train = create_training_data()

    _, benchmark = train_model_b(
        X_train,
        y_train,
    )

    assert (
        benchmark["number_of_categories"]
        == y_train.nunique()
    )


def test_model_a_records_tfidf_vocabulary_size():
    X_train, y_train = create_training_data()

    _, benchmark = train_model_a(
        X_train,
        y_train,
    )

    assert (
        benchmark["tfidf_vocabulary_size"] > 0
    )


def test_model_b_records_tfidf_vocabulary_size():
    X_train, y_train = create_training_data()

    _, benchmark = train_model_b(
        X_train,
        y_train,
    )

    assert (
        benchmark["tfidf_vocabulary_size"] > 0
    )


def test_model_a_records_model_configuration():
    X_train, y_train = create_training_data()

    _, benchmark = train_model_a(
        X_train,
        y_train,
    )

    configuration = benchmark[
        "model_configuration"
    ]

    assert configuration[
        "max_iterations"
    ] == 1000

    assert configuration[
        "random_state"
    ] == 42


def test_model_b_records_model_configuration():
    X_train, y_train = create_training_data()

    _, benchmark = train_model_b(
        X_train,
        y_train,
    )

    configuration = benchmark[
        "model_configuration"
    ]

    assert configuration[
        "max_iterations"
    ] == 1000

    assert configuration[
        "random_state"
    ] == 42


def test_model_a_records_tfidf_configuration():
    X_train, y_train = create_training_data()

    _, benchmark = train_model_a(
        X_train,
        y_train,
    )

    configuration = benchmark[
        "tfidf_configuration"
    ]

    assert configuration["lowercase"] is True
    assert configuration["ngram_range"] == (1, 2)
    assert configuration["min_df"] == 2
    assert configuration["max_features"] == 5000


def test_model_b_records_tfidf_configuration():
    X_train, y_train = create_training_data()

    _, benchmark = train_model_b(
        X_train,
        y_train,
    )

    configuration = benchmark[
        "tfidf_configuration"
    ]

    assert configuration["lowercase"] is True
    assert configuration["ngram_range"] == (1, 2)
    assert configuration["min_df"] == 2
    assert configuration["max_features"] == 5000


def test_model_a_classifier_has_expected_classes():
    X_train, y_train = create_training_data()

    trained_model, _ = train_model_a(
        X_train,
        y_train,
    )

    expected_classes = set(
        y_train.unique()
    )

    actual_classes = set(
        trained_model.classifier.classes_
    )

    assert actual_classes == expected_classes


def test_model_b_classifier_has_expected_classes():
    X_train, y_train = create_training_data()

    trained_model, _ = train_model_b(
        X_train,
        y_train,
    )

    expected_classes = set(
        y_train.unique()
    )

    actual_classes = set(
        trained_model.classifier.classes_
    )

    assert actual_classes == expected_classes


def test_both_models_use_same_training_sample_count():
    X_train, y_train = create_training_data()

    _, benchmark_a = train_model_a(
        X_train,
        y_train,
    )

    _, benchmark_b = train_model_b(
        X_train,
        y_train,
    )

    assert (
        benchmark_a["training_sample_count"]
        == benchmark_b["training_sample_count"]
    )


def test_both_models_use_same_number_of_categories():
    X_train, y_train = create_training_data()

    _, benchmark_a = train_model_a(
        X_train,
        y_train,
    )

    _, benchmark_b = train_model_b(
        X_train,
        y_train,
    )

    assert (
        benchmark_a["number_of_categories"]
        == benchmark_b["number_of_categories"]
    )


def test_model_a_trains_successfully():
    X_train, y_train = create_training_data()

    trained_model, _ = train_model_a(
        X_train,
        y_train,
    )

    assert trained_model.classifier is not None
    assert trained_model.feature_pipeline is not None


def test_model_b_trains_successfully():
    X_train, y_train = create_training_data()

    trained_model, _ = train_model_b(
        X_train,
        y_train,
    )

    assert trained_model.classifier is not None
    assert trained_model.feature_pipeline is not None