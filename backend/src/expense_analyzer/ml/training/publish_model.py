from pathlib import Path

from expense_analyzer.ml.datasets.pipeline import (
    DatasetPreparationPipeline,
)
from expense_analyzer.ml.evaluation.evaluator import (
    ModelEvaluator,
)
from expense_analyzer.ml.models.metadata import (
    WinningModelDecision,
    create_artifact_metadata,
)
from expense_analyzer.ml.models.model_bundle import (
    ModelBundle,
)
from expense_analyzer.ml.models.naming import (
    EXPENSE_CATEGORY_MODEL_NAME,
)
from expense_analyzer.ml.models.persistence import (
    ModelPersistenceService,
)
from expense_analyzer.ml.training.train_baseline import (
    train_model_a,
)


MODEL_VERSION = "v1.0.0"
ARTIFACTS_DIRECTORY = Path("artifacts/models")


def publish_model() -> Path:
    print("=" * 60)
    print("Expense Category Model Publishing")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Prepare the dataset using the existing project
    #    training pipeline.
    # ---------------------------------------------------------
    print("\n[1/6] Preparing dataset...")

    dataset = DatasetPreparationPipeline().prepare()

    print(
        f"Training rows : {len(dataset.X_train)}"
    )
    print(
        f"Test rows     : {len(dataset.X_test)}"
    )
    print(
        f"Categories    : {dataset.y_train.nunique()}"
    )

    # ---------------------------------------------------------
    # 2. Train the existing Model A.
    # ---------------------------------------------------------
    print("\n[2/6] Training Model A...")

    trained_model, benchmark = train_model_a(
        X_train=dataset.X_train,
        y_train=dataset.y_train,
        test_row_count=len(dataset.X_test),
    )

    experiment = benchmark["experiment"]

    print(
        "Model trained successfully."
    )

    # ---------------------------------------------------------
    # 3. Evaluate using the existing evaluation framework.
    #    IMPORTANT: test data only.
    # ---------------------------------------------------------
    print("\n[3/6] Evaluating model...")

    labels = sorted(
        dataset.y_test.astype(str).unique()
    )

    evaluator = ModelEvaluator()

    evaluation_metrics = evaluator.evaluate(
        model=trained_model,
        model_name="Model A",
        X_test=dataset.X_test,
        y_test=dataset.y_test,
        labels=labels,
    )

    print(
        f"Accuracy       : {evaluation_metrics.accuracy:.4f}"
    )
    print(
        f"Macro Precision: "
        f"{evaluation_metrics.macro_precision:.4f}"
    )
    print(
        f"Macro Recall   : "
        f"{evaluation_metrics.macro_recall:.4f}"
    )
    print(
        f"Macro F1       : "
        f"{evaluation_metrics.macro_f1:.4f}"
    )

    # ---------------------------------------------------------
    # 4. Record the publishing decision.
    #
    # This is the metadata required by your current
    # ModelArtifactMetadata structure.
    # ---------------------------------------------------------
    print("\n[4/6] Creating artifact metadata...")

    decision = WinningModelDecision(
        selected_model_name="Model A",
        selection_metric="macro_f1",
        selection_reason=(
            "Model A is published as the expense category "
            "inference model for version v1.0.0."
        ),
        phase_6_report_path="",
        decided_at="",
    )

    metadata = create_artifact_metadata(
        model_name=EXPENSE_CATEGORY_MODEL_NAME,
        model_version=MODEL_VERSION,
        experiment=experiment,
        evaluation_metrics=evaluation_metrics,
        decision=decision,
        X_train=dataset.X_train,
        y_train=dataset.y_train,
    )

    # ---------------------------------------------------------
    # 5. Build complete model bundle.
    # ---------------------------------------------------------
    print("\n[5/6] Building model bundle...")

    bundle = ModelBundle(
        feature_pipeline=trained_model.feature_pipeline,
        classifier=trained_model.classifier,
        metadata=metadata,
    )

    # ---------------------------------------------------------
    # 6. Persist through the existing persistence service.
    #
    # This creates:
    #
    # artifacts/models/
    #   expense_category/
    #       v1.0.0/
    #           model.joblib
    #           metadata.json
    #
    # and registers the model.
    # ---------------------------------------------------------
    print("\n[6/6] Publishing model bundle...")

    persistence = ModelPersistenceService(
        artifacts_directory=ARTIFACTS_DIRECTORY
    )

    artifact_directory = persistence.save_bundle(
        bundle
    )

    print("\n" + "=" * 60)
    print("MODEL PUBLISHED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"Model directory : {artifact_directory}"
    )
    print(
        f"Model file      : "
        f"{artifact_directory / 'model.joblib'}"
    )
    print(
        f"Metadata file   : "
        f"{artifact_directory / 'metadata.json'}"
    )

    return artifact_directory


def main() -> None:
    publish_model()


if __name__ == "__main__":
    main()