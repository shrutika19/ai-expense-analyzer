import json

import numpy as np
import pandas as pd
import pytest

from expense_analyzer.ml.evaluation.result import (
    ModelEvaluationResult,
    PerCategoryMetrics,
)
from expense_analyzer.ml.models.loader import ModelBundleLoader
from expense_analyzer.ml.models.metadata import (
    ModelArtifactMetadata,
    WinningModelDecision,
    create_training_dataset_identifier,
)
from expense_analyzer.ml.models.model_bundle import ModelBundle
from expense_analyzer.ml.models.persistence import (
    ModelPersistenceService,
)
from expense_analyzer.ml.training.trainer import CategoryModelTrainer


def create_evaluation_metrics() -> ModelEvaluationResult:
    return ModelEvaluationResult(
        model_name="Model B: TF-IDF + Amount",
        accuracy=1.0,
        macro_precision=1.0,
        macro_recall=1.0,
        macro_f1=1.0,
        weighted_precision=1.0,
        weighted_recall=1.0,
        weighted_f1=1.0,
        per_category_metrics=(
            PerCategoryMetrics("Food", 1.0, 1.0, 1.0),
            PerCategoryMetrics("Transport", 1.0, 1.0, 1.0),
        ),
        confusion_matrix=((2, 0), (0, 2)),
        labels=("Food", "Transport"),
    )


def create_saved_bundle(tmp_path):
    X_train = pd.DataFrame(
        {
            "description": [
                "restaurant lunch",
                "restaurant dinner",
                "bus ticket",
                "bus ride",
            ],
            "amount": [25, 40, 5, 8],
        }
    )
    y_train = pd.Series(
        ["Food", "Food", "Transport", "Transport"],
        name="category",
    )
    trained_model = CategoryModelTrainer().train(X_train, y_train)
    metadata = ModelArtifactMetadata(
        model_name="expense_category",
        model_version="v1.0.0",
        algorithm="LogisticRegression",
        feature_configuration={"amount_included": True},
        training_dataset_identifier=create_training_dataset_identifier(
            X_train,
            y_train,
        ),
        training_row_count=len(X_train),
        number_of_categories=2,
        category_labels=("Food", "Transport"),
        training_timestamp="2026-09-15T00:00:00+00:00",
        random_seed=42,
        model_parameters={"max_iterations": 1000},
        evaluation_metrics=create_evaluation_metrics(),
        confidence_threshold=None,
        winning_model_decision=WinningModelDecision(
            selected_model_name="baseline_tfidf_logistic_model_b",
            selection_metric="macro_f1",
            selection_reason="Model B won the held-out comparison.",
            phase_6_report_path="artifacts/reports/baseline.json",
            decided_at="2026-09-15T00:00:00+00:00",
        ),
    )
    bundle = ModelBundle(
        feature_pipeline=trained_model.feature_pipeline,
        classifier=trained_model.classifier,
        metadata=metadata,
    )
    ModelPersistenceService(tmp_path).save_bundle(bundle)
    return bundle


def test_loader_reconstructs_bundle_with_metadata(tmp_path):
    original_bundle = create_saved_bundle(tmp_path)

    loaded_bundle = ModelBundleLoader(tmp_path).load(
        "expense_category",
        "v1.0.0",
    )

    assert loaded_bundle.metadata == original_bundle.metadata.__class__(
        **{
            **original_bundle.metadata.__dict__,
            "model_checksum": loaded_bundle.metadata.model_checksum,
        }
    )
    assert loaded_bundle.feature_pipeline.include_amount is True


def test_complete_persistence_flow_reproduces_predictions_and_probabilities(
    tmp_path,
):
    original_bundle = create_saved_bundle(tmp_path)
    loaded_bundle = ModelBundleLoader(tmp_path).load(
        "expense_category",
        "v1.0.0",
    )
    X_test = pd.DataFrame(
        {
            "description": ["restaurant meal", "bus commute"],
            "amount": [30, 6],
        }
    )

    original_features = original_bundle.feature_pipeline.transform(X_test)
    loaded_features = loaded_bundle.feature_pipeline.transform(X_test)
    prediction_before = original_bundle.classifier.predict(original_features)
    prediction_after = loaded_bundle.classifier.predict(loaded_features)
    probabilities_before = original_bundle.classifier.predict_proba(
        original_features
    )
    probabilities_after = loaded_bundle.classifier.predict_proba(
        loaded_features
    )

    assert prediction_before.tolist() == prediction_after.tolist()
    np.testing.assert_allclose(
        probabilities_before,
        probabilities_after,
        rtol=1e-12,
        atol=1e-12,
    )


def test_loaded_pipeline_reproduces_training_feature_vectors(tmp_path):
    original_bundle = create_saved_bundle(tmp_path)
    loaded_bundle = ModelBundleLoader(tmp_path).load(
        "expense_category",
        "v1.0.0",
    )
    raw_input = pd.DataFrame(
        {
            "description": ["restaurant meal", "bus commute"],
            "amount": [30, 6],
        }
    )

    original_features = original_bundle.feature_pipeline.transform(raw_input)
    loaded_features = loaded_bundle.feature_pipeline.transform(raw_input)

    np.testing.assert_allclose(
        original_features.toarray(),
        loaded_features.toarray(),
        rtol=1e-12,
        atol=1e-12,
    )


def test_loader_rejects_missing_wrong_corrupt_and_invalid_artifacts(tmp_path):
    loader = ModelBundleLoader(tmp_path)

    with pytest.raises(FileNotFoundError):
        loader.load("expense_category", "v1.0.0")

    create_saved_bundle(tmp_path)

    with pytest.raises(FileNotFoundError):
        loader.load("expense_category", "v9.0.0")

    metadata_path = (
        tmp_path / "expense_category" / "v1.0.0" / "metadata.json"
    )
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["algorithm"] = "InvalidAlgorithm"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(ValueError, match="algorithm"):
        loader.load("expense_category", "v1.0.0")

    metadata["algorithm"] = "LogisticRegression"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    model_path = tmp_path / "expense_category" / "v1.0.0" / "model.joblib"
    model_path.write_bytes(b"corrupted")

    with pytest.raises(ValueError, match="checksum"):
        loader.load("expense_category", "v1.0.0")


def test_loader_rejects_incompatible_runtime_environment(tmp_path):
    create_saved_bundle(tmp_path)
    metadata_path = (
        tmp_path / "expense_category" / "v1.0.0" / "metadata.json"
    )
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["runtime_environment"]["scikit_learn"] = "0.24.0"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(ValueError, match="scikit_learn"):
        ModelBundleLoader(tmp_path).load("expense_category", "v1.0.0")