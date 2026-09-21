from dataclasses import dataclass
from typing import Any

from expense_analyzer.ml.training.configuration import (
    TrainingConfiguration,
)


@dataclass(frozen=True)
class ExperimentMetadata:
    """
    Metadata describing a machine-learning training experiment.
    """

    experiment_name: str
    model_type: str
    feature_configuration: dict[str, Any]
    training_row_count: int
    test_row_count: int
    number_of_categories: int
    random_state: int
    model_parameters: dict[str, Any]


def create_experiment_metadata(
    experiment_name: str,
    configuration: TrainingConfiguration,
    training_row_count: int,
    test_row_count: int,
    number_of_categories: int,
) -> ExperimentMetadata:
    """Create a reproducible record for a baseline training run."""

    feature_configuration = {
        "tfidf": {
            "lowercase": configuration.tfidf.lowercase,
            "ngram_range": configuration.tfidf.ngram_range,
            "min_df": configuration.tfidf.min_df,
            "max_features": configuration.tfidf.max_features,
        },
        "amount_included": configuration.include_amount,
    }

    model_parameters = {
        "max_iterations": configuration.model.max_iterations,
        "random_state": configuration.model.random_state,
    }

    return ExperimentMetadata(
        experiment_name=experiment_name,
        model_type="LogisticRegression",
        feature_configuration=feature_configuration,
        training_row_count=training_row_count,
        test_row_count=test_row_count,
        number_of_categories=number_of_categories,
        random_state=configuration.model.random_state,
        model_parameters=model_parameters,
    )