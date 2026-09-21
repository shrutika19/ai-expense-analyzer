from dataclasses import replace
import json

import pandas as pd
import pytest
from pathlib import Path

from expense_analyzer.ml.evaluation.comparison import ModelComparison
from expense_analyzer.ml.evaluation.result import (
    ModelEvaluationResult,
    PerCategoryMetrics,
)
from expense_analyzer.ml.models.loader import ModelBundleLoader
from expense_analyzer.ml.models.metadata import (
    ModelArtifactMetadata,
    WinningModelDecision,
    create_training_dataset_identifier,
    create_winning_model_decision,
)
from expense_analyzer.ml.models.model_bundle import (
    ModelBundle,
    ModelBundleStorage,
)
from expense_analyzer.ml.models.persistence import (
    ModelPersistenceService,
)


def create_evaluation_result(macro_f1: float) -> ModelEvaluationResult:
    return ModelEvaluationResult(
        model_name="Model",
        accuracy=macro_f1,
        macro_precision=macro_f1,
        macro_recall=macro_f1,
        macro_f1=macro_f1,
        weighted_precision=macro_f1,
        weighted_recall=macro_f1,
        weighted_f1=macro_f1,
        per_category_metrics=(
            PerCategoryMetrics("Food", macro_f1, macro_f1, macro_f1),
            PerCategoryMetrics(
                "Transport",
                macro_f1,
                macro_f1,
                macro_f1,
            ),
        ),
        confusion_matrix=((1, 0), (0, 1)),
        labels=("Food", "Transport"),
    )


def create_bundle(version: str) -> ModelBundle:
    metrics = create_evaluation_result(0.8)
    decision = WinningModelDecision(
        selected_model_name="baseline_tfidf_logistic_model_b",
        selection_metric="macro_f1",
        selection_reason="Model B has the stronger macro F1.",
        phase_6_report_path="artifacts/reports/baseline.json",
        decided_at="2026-09-15T00:00:00+00:00",
    )
    metadata = ModelArtifactMetadata(
        model_name="expense_category",
        model_version=version,
        algorithm="LogisticRegression",
        feature_configuration={"amount_included": True},
        training_dataset_identifier="dataset-fingerprint",
        training_row_count=10,
        number_of_categories=2,
        category_labels=("Food", "Transport"),
        training_timestamp="2026-09-15T00:00:00+00:00",
        random_seed=42,
        model_parameters={"max_iterations": 1000},
        evaluation_metrics=metrics,
        confidence_threshold=None,
        winning_model_decision=decision,
    )
    return ModelBundle(
        classifier={"classifier": "stored"},
        feature_pipeline={"pipeline": "stored"},
        metadata=metadata,
    )


def test_dataset_identifier_is_deterministic_and_data_sensitive():
    X_train = pd.DataFrame(
        {"description": ["lunch", "bus"], "amount": [20, 10]}
    )
    y_train = pd.Series(["Food", "Transport"], name="category")

    identifier = create_training_dataset_identifier(X_train, y_train)

    assert identifier == create_training_dataset_identifier(X_train, y_train)
    assert identifier != create_training_dataset_identifier(
        X_train.assign(amount=[21, 10]),
        y_train,
    )


def test_winning_decision_uses_macro_f1_and_rejects_ties():
    comparison = ModelComparison(
        model_a_metrics=create_evaluation_result(0.7),
        model_b_metrics=create_evaluation_result(0.8),
    )

    decision = create_winning_model_decision(comparison, "report.json")

    assert decision.selected_model_name == comparison.model_b_name

    with pytest.raises(ValueError, match="tied"):
        create_winning_model_decision(
            replace(
                comparison,
                model_b_metrics=create_evaluation_result(0.7),
            ),
            "report.json",
        )


def test_model_bundle_round_trip_and_latest_version(tmp_path):
    storage = ModelBundleStorage(tmp_path)
    storage.save(create_bundle("v1.0.0"))
    storage.save(create_bundle("v1.1.0"))

    loader = ModelBundleLoader(tmp_path)
    loaded = loader.load("expense_category", "v1.0.0")
    latest = loader.load("expense_category")

    assert loaded.classifier == {"classifier": "stored"}
    assert loaded.feature_pipeline == {
        "pipeline": "stored"
    }
    assert loaded.metadata.model_checksum is not None
    assert set(loaded.metadata.runtime_environment) == {
        "python",
        "scikit_learn",
        "pandas",
    }
    assert all(loaded.metadata.runtime_environment.values())
    assert latest.metadata.model_version == "v1.1.0"


def test_model_bundle_rejects_duplicate_versions_and_corruption(tmp_path):
    storage = ModelBundleStorage(tmp_path)
    storage.save(create_bundle("v1.0.0"))

    with pytest.raises(FileExistsError):
        storage.save(create_bundle("v1.0.0"))

    model_path = tmp_path / "expense_category" / "v1.0.0" / "model.joblib"
    model_path.write_bytes(b"corrupted")

    with pytest.raises(ValueError, match="checksum"):
        ModelBundleLoader(tmp_path).load("expense_category", "v1.0.0")


def test_persistence_service_saves_checks_and_loads_bundle(tmp_path):
    service = ModelPersistenceService(tmp_path)
    bundle = create_bundle("v1.0.0")

    assert service.artifact_exists(
        "expense_category",
        "v1.0.0",
    ) is False

    service.save_bundle(bundle)
    loaded = service.load_bundle("expense_category", "v1.0.0")

    assert service.artifact_exists(
        "expense_category",
        "v1.0.0",
    ) is True
    assert loaded.classifier == bundle.classifier
    assert loaded.feature_pipeline == bundle.feature_pipeline


def test_persistence_service_registers_validated_model(tmp_path):
    service = ModelPersistenceService(tmp_path)

    service.save_bundle(create_bundle("v1.0.0"))
    entry = service.registry.get_entry("expense_category", "v1.0.0")

    assert entry.status == "validated"
    assert Path(entry.artifact_location) == tmp_path / "expense_category" / "v1.0.0"
    assert entry.metrics["macro_f1"] == 0.8

    with pytest.raises(ValueError, match="inference testing"):
        service.registry.update_status(
            "expense_category",
            "v1.0.0",
            "production",
        )

    assert service.registry.update_status(
        "expense_category",
        "v1.0.0",
        "production",
        inference_tested=True,
    ).status == "production"


@pytest.mark.parametrize(
    ("metadata_change", "message"),
    [
        ({"algorithm": "RandomForest"}, "algorithm"),
        ({"feature_configuration": {}}, "feature configuration"),
        ({"category_labels": ("Food",)}, "category labels"),
    ],
)
def test_persistence_service_rejects_invalid_metadata(
    tmp_path,
    metadata_change,
    message,
):
    bundle = create_bundle("v1.0.0")
    invalid_bundle = replace(
        bundle,
        metadata=replace(bundle.metadata, **metadata_change),
    )

    with pytest.raises(ValueError, match=message):
        ModelPersistenceService(tmp_path).save_bundle(invalid_bundle)


def test_loader_rejects_invalid_metadata_from_artifact(tmp_path):
    storage = ModelBundleStorage(tmp_path)
    storage.save(create_bundle("v1.0.0"))
    metadata_path = (
        tmp_path
        / "expense_category"
        / "v1.0.0"
        / "metadata.json"
    )
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["feature_configuration"] = {}
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(ValueError, match="feature configuration"):
        ModelBundleLoader(tmp_path).load("expense_category", "v1.0.0")


@pytest.mark.parametrize("version", ["1.0.0", "v1.0", "v1.0.0-beta"])
def test_model_bundle_requires_v_prefixed_semantic_version(tmp_path, version):
    with pytest.raises(ValueError, match="vX.Y.Z"):
        ModelBundleStorage(tmp_path).save(create_bundle(version))


def test_model_bundle_requires_canonical_artifact_name(tmp_path):
    bundle = create_bundle("v1.0.0")
    invalid_bundle = replace(
        bundle,
        metadata=replace(bundle.metadata, model_name="latest"),
    )

    with pytest.raises(ValueError, match="expense_category"):
        ModelBundleStorage(tmp_path).save(invalid_bundle)