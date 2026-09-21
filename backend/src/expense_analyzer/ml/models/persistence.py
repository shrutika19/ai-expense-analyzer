from pathlib import Path

from expense_analyzer.ml.models.loader import ModelBundleLoader
from expense_analyzer.ml.models.metadata import (
    ModelArtifactMetadata,
    validate_artifact_metadata,
)
from expense_analyzer.ml.models.model_bundle import (
    ModelBundle,
    ModelBundleStorage,
)
from expense_analyzer.ml.models.naming import (
    get_bundle_directory,
)
from expense_analyzer.ml.models.registry import ModelRegistry


class ModelPersistenceService:
    """Persist and reconstruct complete, versioned model bundles."""

    def __init__(
        self,
        artifacts_directory: Path | str = "artifacts/models",
    ) -> None:
        self.artifacts_directory = Path(artifacts_directory)
        self.storage = ModelBundleStorage(self.artifacts_directory)
        self.loader = ModelBundleLoader(self.artifacts_directory)
        self.registry = ModelRegistry(self.artifacts_directory)

    def save_bundle(self, bundle: ModelBundle) -> Path:
        self._validate_metadata(bundle.metadata)
        artifact_directory = self.storage.save(bundle)
        self.registry.register_validated_model(
            metadata=bundle.metadata,
            artifact_directory=artifact_directory,
        )
        return artifact_directory

    def load_bundle(
        self,
        model_name: str,
        model_version: str | None = None,
    ) -> ModelBundle:
        bundle = self.loader.load(model_name, model_version)
        self._validate_metadata(bundle.metadata)
        return bundle

    def artifact_exists(
        self,
        model_name: str,
        model_version: str,
    ) -> bool:
        bundle_directory = get_bundle_directory(
            self.artifacts_directory,
            model_name,
            model_version,
        )
        return (
            bundle_directory / ModelBundleStorage.MODEL_FILENAME
        ).is_file() and (
            bundle_directory / ModelBundleStorage.METADATA_FILENAME
        ).is_file()

    @staticmethod
    def _validate_metadata(
        metadata: ModelArtifactMetadata,
    ) -> None:
        validate_artifact_metadata(metadata)