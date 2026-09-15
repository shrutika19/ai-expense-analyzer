from dataclasses import dataclass
from typing import Any


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