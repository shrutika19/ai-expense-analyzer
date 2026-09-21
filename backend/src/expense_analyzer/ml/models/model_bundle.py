from dataclasses import dataclass, replace
import hashlib
from pathlib import Path
import tempfile

import joblib

from expense_analyzer.ml.models.metadata import (
    ModelArtifactMetadata,
    serialize_artifact_metadata,
)
from expense_analyzer.ml.models.naming import (
    get_bundle_directory,
)
from expense_analyzer.ml.training.trainer import TrainedModel


@dataclass(frozen=True)
class ModelBundle:
    feature_pipeline: object
    classifier: object
    metadata: ModelArtifactMetadata


class ModelBundleStorage:
    MODEL_FILENAME = "model.joblib"
    METADATA_FILENAME = "metadata.json"

    def __init__(
        self,
        artifacts_directory: Path | str = "artifacts/models",
    ) -> None:
        self.artifacts_directory = Path(artifacts_directory)

    def save(self, bundle: ModelBundle) -> Path:
        metadata = bundle.metadata
        if bundle.classifier is None:
            raise ValueError("Model bundle must include a trained classifier.")
        if bundle.feature_pipeline is None:
            raise ValueError(
                "Model bundle must include a fitted feature pipeline."
            )
        bundle_directory = get_bundle_directory(
            self.artifacts_directory,
            metadata.model_name,
            metadata.model_version,
        )
        if bundle_directory.exists():
            raise FileExistsError(
                f"Model bundle already exists: {bundle_directory}"
            )

        bundle_directory.mkdir(parents=True)
        model_path = bundle_directory / self.MODEL_FILENAME
        self._write_model(
            TrainedModel(
                classifier=bundle.classifier,
                feature_pipeline=bundle.feature_pipeline,
            ),
            model_path,
        )
        checksum = self._calculate_checksum(model_path)
        metadata_path = bundle_directory / self.METADATA_FILENAME
        metadata_path.write_text(
            serialize_artifact_metadata(
                replace(metadata, model_checksum=checksum)
            ),
            encoding="utf-8",
        )
        return bundle_directory

    def _write_model(
        self,
        trained_model: TrainedModel,
        model_path: Path,
    ) -> None:
        with tempfile.NamedTemporaryFile(
            dir=model_path.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

        try:
            joblib.dump(trained_model, temporary_path)
            temporary_path.replace(model_path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()

    @staticmethod
    def _calculate_checksum(model_path: Path) -> str:
        return hashlib.sha256(model_path.read_bytes()).hexdigest()