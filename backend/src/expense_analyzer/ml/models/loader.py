import hashlib
from pathlib import Path

import joblib

from expense_analyzer.ml.models.metadata import (
    deserialize_artifact_metadata,
    validate_artifact_metadata,
    validate_runtime_compatibility,
)
from expense_analyzer.ml.models.model_bundle import ModelBundle
from expense_analyzer.ml.models.naming import get_bundle_directory


class ModelBundleLoader:
    MODEL_FILENAME = "model.joblib"
    METADATA_FILENAME = "metadata.json"

    def __init__(
        self,
        artifacts_directory: Path | str = "artifacts/models",
    ) -> None:
        self.artifacts_directory = Path(artifacts_directory)

    def load(
        self,
        model_name: str,
        model_version: str | None = None,
    ) -> ModelBundle:
        bundle_directory = self._get_bundle_directory(
            model_name,
            model_version,
        )
        metadata_path = bundle_directory / self.METADATA_FILENAME
        model_path = bundle_directory / self.MODEL_FILENAME

        if not metadata_path.exists() or not model_path.exists():
            raise FileNotFoundError(
                f"Incomplete model bundle: {bundle_directory}"
            )

        try:
            metadata = deserialize_artifact_metadata(
                metadata_path.read_text(encoding="utf-8")
            )
        except (OSError, TypeError, ValueError, KeyError) as error:
            raise ValueError(
                f"Model metadata is not readable: {metadata_path}"
            ) from error

        if metadata.model_name != model_name:
            raise ValueError("Model metadata name does not match the artifact path.")
        if metadata.model_version != bundle_directory.name:
            raise ValueError(
                "Model metadata version does not match the artifact path."
            )
        validate_artifact_metadata(metadata)
        validate_runtime_compatibility(metadata)

        try:
            checksum = hashlib.sha256(model_path.read_bytes()).hexdigest()
        except OSError as error:
            raise ValueError(
                f"Model artifact is not readable: {model_path}"
            ) from error
        if checksum != metadata.model_checksum:
            raise ValueError("Model bundle checksum does not match metadata.")

        try:
            trained_model = joblib.load(model_path)
        except Exception as error:
            raise ValueError(
                f"Model artifact is not readable: {model_path}"
            ) from error

        if (
            not hasattr(trained_model, "classifier")
            or not hasattr(trained_model, "feature_pipeline")
            or trained_model.classifier is None
            or trained_model.feature_pipeline is None
        ):
            raise ValueError(
                "Model artifact does not contain a complete model bundle."
            )

        return ModelBundle(
            classifier=trained_model.classifier,
            feature_pipeline=trained_model.feature_pipeline,
            metadata=metadata,
        )

    def _get_bundle_directory(
        self,
        model_name: str,
        model_version: str | None,
    ) -> Path:
        model_directory = self.artifacts_directory / model_name
        if not model_directory.exists():
            raise FileNotFoundError(f"Model not found: {model_name}")

        version = model_version or self._get_latest_version(model_directory)
        return get_bundle_directory(
            self.artifacts_directory,
            model_name,
            version,
        )

    @staticmethod
    def _get_latest_version(model_directory: Path) -> str:
        versions = [
            path.name
            for path in model_directory.iterdir()
            if path.is_dir()
        ]
        if not versions:
            raise FileNotFoundError(
                f"No model versions found in {model_directory}"
            )

        return max(
            versions,
            key=lambda version: tuple(
                int(part)
                for part in version.removeprefix("v").split(".")
            ),
        )