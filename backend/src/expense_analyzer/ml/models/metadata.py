from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import platform
from typing import Any

import pandas as pd

from expense_analyzer.ml.evaluation.comparison import (
    ModelComparison,
    get_macro_f1_winner,
)
from expense_analyzer.ml.evaluation.result import (
    ConfidenceSummary,
    ConfusionPair,
    EvaluatedPrediction,
    ModelEvaluationResult,
    PerCategoryMetrics,
)
from expense_analyzer.ml.training.experiment import (
    ExperimentMetadata,
)
from expense_analyzer.ml.models.naming import (
    EXPENSE_CATEGORY_MODEL_NAME,
    SEMANTIC_VERSION_PATTERN,
)


@dataclass(frozen=True)
class WinningModelDecision:
    selected_model_name: str
    selection_metric: str
    selection_reason: str
    phase_6_report_path: str
    decided_at: str


@dataclass(frozen=True)
class ModelArtifactMetadata:
    model_name: str
    model_version: str
    algorithm: str
    feature_configuration: dict[str, Any]
    training_dataset_identifier: str
    training_row_count: int
    number_of_categories: int
    category_labels: tuple[str, ...]
    training_timestamp: str
    random_seed: int
    model_parameters: dict[str, Any]
    evaluation_metrics: ModelEvaluationResult
    confidence_threshold: float | None
    winning_model_decision: WinningModelDecision
    model_checksum: str | None = None
    runtime_environment: dict[str, str] = field(
        default_factory=lambda: create_runtime_environment()
    )


def create_runtime_environment() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "scikit_learn": version("scikit-learn"),
        "pandas": version("pandas"),
    }


def validate_runtime_compatibility(
    metadata: ModelArtifactMetadata,
) -> None:
    current_environment = create_runtime_environment()

    for dependency in ("python", "scikit_learn", "pandas"):
        artifact_version = metadata.runtime_environment[dependency]
        current_version = current_environment[dependency]
        if _major_minor(artifact_version) != _major_minor(current_version):
            raise ValueError(
                f"Model artifact requires {dependency} "
                f"{artifact_version}, but the current environment uses "
                f"{current_version}."
            )


def _major_minor(version_string: str) -> tuple[str, str]:
    version_parts = version_string.split(".")
    if len(version_parts) < 2:
        raise ValueError(
            f"Invalid dependency version in model metadata: {version_string}"
        )
    return version_parts[0], version_parts[1]


def validate_artifact_metadata(
    metadata: ModelArtifactMetadata,
) -> None:
    if metadata.model_name != EXPENSE_CATEGORY_MODEL_NAME:
        raise ValueError(
            "Model metadata must use the 'expense_category' model name."
        )
    if not SEMANTIC_VERSION_PATTERN.fullmatch(metadata.model_version):
        raise ValueError(
            "Model metadata version must use vMAJOR.MINOR.PATCH."
        )
    if metadata.algorithm != "LogisticRegression":
        raise ValueError(
            "Model metadata algorithm must be LogisticRegression."
        )
    if not metadata.feature_configuration:
        raise ValueError(
            "Model metadata must include a feature configuration."
        )
    if metadata.training_row_count <= 0:
        raise ValueError(
            "Model metadata training row count must be positive."
        )
    if metadata.number_of_categories < 2:
        raise ValueError(
            "Model metadata must contain at least two categories."
        )
    if len(metadata.category_labels) != metadata.number_of_categories:
        raise ValueError(
            "Model metadata category labels must match the category count."
        )
    if not metadata.training_dataset_identifier:
        raise ValueError(
            "Model metadata must include a dataset identifier."
        )
    required_runtime_versions = {
        "python",
        "scikit_learn",
        "pandas",
    }
    if (
        not required_runtime_versions <= set(metadata.runtime_environment)
        or any(
            not metadata.runtime_environment[version_name]
            for version_name in required_runtime_versions
        )
    ):
        raise ValueError(
            "Model metadata must include Python, scikit-learn, "
            "and pandas versions."
        )


def create_training_dataset_identifier(
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> str:
    if len(X_train) != len(y_train):
        raise ValueError(
            "Training features and target must have the same number of rows."
        )

    dataframe = X_train.copy()
    dataframe["category"] = y_train.to_numpy()
    canonical_data = dataframe.to_json(
        orient="split",
        date_format="iso",
        double_precision=15,
    )
    return hashlib.sha256(canonical_data.encode("utf-8")).hexdigest()


def create_winning_model_decision(
    comparison: ModelComparison,
    phase_6_report_path: str,
) -> WinningModelDecision:
    winner = get_macro_f1_winner(comparison)
    if winner is None:
        raise ValueError("Both baseline evaluation results are required.")
    if winner == "Tie":
        raise ValueError(
            "Macro F1 is tied; choose a model with a documented override."
        )

    model_name = (
        comparison.model_a_name
        if winner == "Model A"
        else comparison.model_b_name
    )
    selected_metrics = (
        comparison.model_a_metrics
        if winner == "Model A"
        else comparison.model_b_metrics
    )
    other_metrics = (
        comparison.model_b_metrics
        if winner == "Model A"
        else comparison.model_a_metrics
    )

    return WinningModelDecision(
        selected_model_name=model_name,
        selection_metric="macro_f1",
        selection_reason=(
            f"Macro F1 {selected_metrics.macro_f1:.4f} exceeds "
            f"the alternate baseline at {other_metrics.macro_f1:.4f}."
        ),
        phase_6_report_path=phase_6_report_path,
        decided_at=datetime.now(timezone.utc).isoformat(),
    )


def create_artifact_metadata(
    model_name: str,
    model_version: str,
    experiment: ExperimentMetadata,
    evaluation_metrics: ModelEvaluationResult,
    decision: WinningModelDecision,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    confidence_threshold: float | None = None,
) -> ModelArtifactMetadata:
    if confidence_threshold is not None and not 0.0 <= confidence_threshold <= 1.0:
        raise ValueError("Confidence threshold must be in [0, 1].")

    return ModelArtifactMetadata(
        model_name=model_name,
        model_version=model_version,
        algorithm=experiment.model_type,
        feature_configuration=experiment.feature_configuration,
        training_dataset_identifier=create_training_dataset_identifier(
            X_train,
            y_train,
        ),
        training_row_count=experiment.training_row_count,
        number_of_categories=experiment.number_of_categories,
        category_labels=evaluation_metrics.labels,
        training_timestamp=datetime.now(timezone.utc).isoformat(),
        random_seed=experiment.random_state,
        model_parameters=experiment.model_parameters,
        evaluation_metrics=evaluation_metrics,
        confidence_threshold=confidence_threshold,
        winning_model_decision=decision,
    )


def serialize_artifact_metadata(
    metadata: ModelArtifactMetadata,
) -> str:
    return json.dumps(asdict(metadata), indent=2)


def deserialize_artifact_metadata(
    serialized_metadata: str,
) -> ModelArtifactMetadata:
    payload = json.loads(serialized_metadata)
    metrics = payload["evaluation_metrics"]

    confidence_summary = metrics.get("confidence_summary")
    if confidence_summary is not None:
        confidence_summary = ConfidenceSummary(
            correct_mean=confidence_summary["correct_mean"],
            incorrect_mean=confidence_summary["incorrect_mean"],
            bands=tuple(
                tuple(band)
                for band in confidence_summary["bands"]
            ),
        )

    evaluation_metrics = ModelEvaluationResult(
        model_name=metrics["model_name"],
        accuracy=metrics["accuracy"],
        macro_precision=metrics["macro_precision"],
        macro_recall=metrics["macro_recall"],
        macro_f1=metrics["macro_f1"],
        weighted_precision=metrics["weighted_precision"],
        weighted_recall=metrics["weighted_recall"],
        weighted_f1=metrics["weighted_f1"],
        per_category_metrics=tuple(
            PerCategoryMetrics(**metric)
            for metric in metrics["per_category_metrics"]
        ),
        confusion_matrix=tuple(
            tuple(row)
            for row in metrics["confusion_matrix"]
        ),
        labels=tuple(metrics["labels"]),
        evaluated_predictions=tuple(
            EvaluatedPrediction(**prediction)
            for prediction in metrics.get("evaluated_predictions", [])
        ),
        confidence_summary=confidence_summary,
        top_confusions=tuple(
            ConfusionPair(**pair)
            for pair in metrics.get("top_confusions", [])
        ),
    )

    return ModelArtifactMetadata(
        model_name=payload["model_name"],
        model_version=payload["model_version"],
        algorithm=payload["algorithm"],
        feature_configuration=payload["feature_configuration"],
        training_dataset_identifier=payload["training_dataset_identifier"],
        training_row_count=payload["training_row_count"],
        number_of_categories=payload["number_of_categories"],
        category_labels=tuple(payload["category_labels"]),
        training_timestamp=payload["training_timestamp"],
        random_seed=payload["random_seed"],
        model_parameters=payload["model_parameters"],
        evaluation_metrics=evaluation_metrics,
        confidence_threshold=payload["confidence_threshold"],
        winning_model_decision=WinningModelDecision(
            **payload["winning_model_decision"]
        ),
        model_checksum=payload["model_checksum"],
        runtime_environment=payload["runtime_environment"],
    )