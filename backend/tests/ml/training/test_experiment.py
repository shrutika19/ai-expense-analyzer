import pytest

from expense_analyzer.ml.training.experiment import (
    ExperimentMetadata,
)


def create_metadata() -> ExperimentMetadata:
    return ExperimentMetadata(
        experiment_name="baseline_tfidf_logistic_model_a",
        model_type="LogisticRegression",
        feature_configuration={
            "text_features": "TF-IDF(description)",
            "amount_included": False,
            "lowercase": True,
            "ngram_range": (1, 2),
            "min_df": 2,
            "max_features": 5000,
        },
        training_row_count=100,
        test_row_count=25,
        number_of_categories=5,
        random_state=42,
        model_parameters={
            "max_iter": 1000,
            "random_state": 42,
        },
    )


def test_experiment_metadata_can_be_created():
    metadata = create_metadata()

    assert isinstance(
        metadata,
        ExperimentMetadata,
    )


def test_experiment_name_is_recorded():
    metadata = create_metadata()

    assert (
        metadata.experiment_name
        == "baseline_tfidf_logistic_model_a"
    )


def test_model_type_is_recorded():
    metadata = create_metadata()

    assert (
        metadata.model_type
        == "LogisticRegression"
    )


def test_feature_configuration_is_recorded():
    metadata = create_metadata()

    assert metadata.feature_configuration == {
        "text_features": "TF-IDF(description)",
        "amount_included": False,
        "lowercase": True,
        "ngram_range": (1, 2),
        "min_df": 2,
        "max_features": 5000,
    }


def test_training_row_count_is_recorded():
    metadata = create_metadata()

    assert metadata.training_row_count == 100


def test_test_row_count_is_recorded():
    metadata = create_metadata()

    assert metadata.test_row_count == 25


def test_number_of_categories_is_recorded():
    metadata = create_metadata()

    assert metadata.number_of_categories == 5


def test_random_state_is_recorded():
    metadata = create_metadata()

    assert metadata.random_state == 42


def test_model_parameters_are_recorded():
    metadata = create_metadata()

    assert metadata.model_parameters == {
        "max_iter": 1000,
        "random_state": 42,
    }


def test_training_and_test_counts_are_independent():
    metadata = create_metadata()

    assert metadata.training_row_count != (
        metadata.test_row_count
    )


def test_model_a_does_not_include_amount():
    metadata = create_metadata()

    assert (
        metadata.feature_configuration[
            "amount_included"
        ]
        is False
    )


def test_model_b_can_record_amount_feature():
    metadata = ExperimentMetadata(
        experiment_name="baseline_tfidf_logistic_model_b",
        model_type="LogisticRegression",
        feature_configuration={
            "text_features": "TF-IDF(description)",
            "numerical_features": ["amount"],
            "amount_included": True,
            "lowercase": True,
            "ngram_range": (1, 2),
            "min_df": 2,
            "max_features": 5000,
        },
        training_row_count=100,
        test_row_count=25,
        number_of_categories=5,
        random_state=42,
        model_parameters={
            "max_iter": 1000,
            "random_state": 42,
        },
    )

    assert (
        metadata.experiment_name
        == "baseline_tfidf_logistic_model_b"
    )

    assert (
        metadata.feature_configuration[
            "amount_included"
        ]
        is True
    )

    assert (
        metadata.feature_configuration[
            "numerical_features"
        ]
        == ["amount"]
    )


def test_experiment_metadata_is_immutable():
    metadata = create_metadata()

    with pytest.raises(
        AttributeError,
    ):
        metadata.training_row_count = 200


def test_experiment_metadata_is_immutable_for_model_type():
    metadata = create_metadata()

    with pytest.raises(
        AttributeError,
    ):
        metadata.model_type = "RandomForest"


def test_experiment_metadata_is_immutable_for_experiment_name():
    metadata = create_metadata()

    with pytest.raises(
        AttributeError,
    ):
        metadata.experiment_name = "another_experiment"