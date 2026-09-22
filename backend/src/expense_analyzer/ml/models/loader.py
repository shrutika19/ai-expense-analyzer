import hashlib
from pathlib import Path

import joblib

from expense_analyzer.ml.exceptions import (
    ModelArtifactNotFoundError,
    ModelCompatibilityError,
    ModelLoadError,
)
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
        self.artifacts_directory = Path(
            artifacts_directory
        )

    def load(
        self,
        model_name: str,
        model_version: str | None = None,
    ) -> ModelBundle:
        """
        Load and validate a persisted model bundle.

        The loader validates:
            - Model artifact existence.
            - Metadata readability.
            - Model name.
            - Model version.
            - Artifact metadata.
            - Runtime compatibility.
            - Artifact checksum.
            - Model bundle structure.
        """

        bundle_directory = self._get_bundle_directory(
            model_name,
            model_version,
        )

        metadata_path = (
            bundle_directory / self.METADATA_FILENAME
        )
        model_path = (
            bundle_directory / self.MODEL_FILENAME
        )

        # ---------------------------------------------------------
        # 1. Validate artifact files exist
        # ---------------------------------------------------------

        if (
            not metadata_path.exists()
            or not model_path.exists()
        ):
            raise ModelArtifactNotFoundError(
                f"Incomplete model bundle: "
                f"{bundle_directory}"
            )

        # ---------------------------------------------------------
        # 2. Read and deserialize metadata
        # ---------------------------------------------------------

        try:
            metadata = deserialize_artifact_metadata(
                metadata_path.read_text(
                    encoding="utf-8"
                )
            )
        except (
            OSError,
            TypeError,
            ValueError,
            KeyError,
        ) as error:
            raise ModelCompatibilityError(
                "Model metadata is not readable: "
                f"{metadata_path}"
            ) from error

        # ---------------------------------------------------------
        # 3. Validate metadata identity
        # ---------------------------------------------------------

        if metadata.model_name != model_name:
            raise ModelCompatibilityError(
                "Model metadata name does not match "
                "the artifact path."
            )

        if (
            metadata.model_version
            != bundle_directory.name
        ):
            raise ModelCompatibilityError(
                "Model metadata version does not match "
                "the artifact path."
            )

        # ---------------------------------------------------------
        # 4. Validate metadata and runtime compatibility
        # ---------------------------------------------------------

        try:
            validate_artifact_metadata(metadata)

            validate_runtime_compatibility(
                metadata
            )

        except Exception as error:
            raise ModelCompatibilityError(
                "Model artifact is incompatible with "
                "the current application."
            ) from error

        # ---------------------------------------------------------
        # 5. Validate model checksum
        # ---------------------------------------------------------

        try:
            checksum = hashlib.sha256(
                model_path.read_bytes()
            ).hexdigest()

        except OSError as error:
            raise ModelLoadError(
                "Model artifact is not readable: "
                f"{model_path}"
            ) from error

        if checksum != metadata.model_checksum:
            raise ModelCompatibilityError(
                "Model bundle checksum does not "
                "match metadata."
            )

        # ---------------------------------------------------------
        # 6. Load model artifact
        # ---------------------------------------------------------

        try:
            trained_model = joblib.load(
                model_path
            )

        except Exception as error:
            raise ModelLoadError(
                "Model artifact could not be loaded: "
                f"{model_path}"
            ) from error

        # ---------------------------------------------------------
        # 7. Validate loaded model structure
        # ---------------------------------------------------------

        if (
            not hasattr(
                trained_model,
                "classifier",
            )
            or not hasattr(
                trained_model,
                "feature_pipeline",
            )
            or trained_model.classifier is None
            or trained_model.feature_pipeline is None
        ):
            raise ModelCompatibilityError(
                "Model artifact does not contain "
                "a complete model bundle."
            )

        # ---------------------------------------------------------
        # 8. Return normalized ModelBundle
        # ---------------------------------------------------------

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
        model_directory = (
            self.artifacts_directory / model_name
        )

        if not model_directory.exists():
            raise ModelArtifactNotFoundError(
                f"Model not found: {model_name}"
            )

        version = (
            model_version
            or self._get_latest_version(
                model_directory
            )
        )

        bundle_directory = get_bundle_directory(
            self.artifacts_directory,
            model_name,
            version,
        )

        if not bundle_directory.exists():
            raise ModelArtifactNotFoundError(
                f"Model version '{version}' not found "
                f"for '{model_name}'."
            )

        return bundle_directory

    @staticmethod
    def _get_latest_version(
        model_directory: Path,
    ) -> str:
        versions = [
            path.name
            for path in model_directory.iterdir()
            if path.is_dir()
        ]

        if not versions:
            raise ModelArtifactNotFoundError(
                f"No model versions found in "
                f"{model_directory}"
            )

        try:
            return max(
                versions,
                key=lambda version: tuple(
                    int(part)
                    for part in version
                    .removeprefix("v")
                    .split(".")
                ),
            )

        except (TypeError, ValueError) as error:
            raise ModelCompatibilityError(
                "Model versions contain an invalid "
                "version format."
            ) from error