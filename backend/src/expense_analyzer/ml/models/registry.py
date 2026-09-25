from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

from expense_analyzer.ml.models.metadata import ModelArtifactMetadata


VALID_MODEL_STATUSES = {
    "candidate",
    "validated",
    "production",
    "previous",
    "retired",
}


@dataclass(frozen=True)
class ModelRegistryEntry:
    model_name: str
    model_version: str
    artifact_location: str
    status: str
    metrics: dict[str, float]
    created_timestamp: str


class ModelRegistry:
    """Maintain lightweight metadata for published model artifacts."""

    REGISTRY_FILENAME = "registry.json"

    def __init__(self, artifacts_directory: Path | str) -> None:
        self.artifacts_directory = Path(artifacts_directory)
        self.registry_path = self.artifacts_directory / self.REGISTRY_FILENAME

    def register_validated_model(
        self,
        metadata: ModelArtifactMetadata,
        artifact_directory: Path,
    ) -> ModelRegistryEntry:
        entry = ModelRegistryEntry(
            model_name=metadata.model_name,
            model_version=metadata.model_version,
            artifact_location=str(artifact_directory),
            status="validated",
            metrics={
                "accuracy": metadata.evaluation_metrics.accuracy,
                "macro_precision": metadata.evaluation_metrics.macro_precision,
                "macro_recall": metadata.evaluation_metrics.macro_recall,
                "macro_f1": metadata.evaluation_metrics.macro_f1,
                "weighted_f1": metadata.evaluation_metrics.weighted_f1,
            },
            created_timestamp=datetime.now(timezone.utc).isoformat(),
        )
        entries = list(self.list_entries())
        if any(
            existing.model_name == entry.model_name
            and existing.model_version == entry.model_version
            for existing in entries
        ):
            raise FileExistsError(
                "A registry entry already exists for "
                f"{entry.model_name} {entry.model_version}."
            )

        entries.append(entry)
        self._write_entries(entries)
        return entry

    def get_entry(
        self,
        model_name: str,
        model_version: str,
    ) -> ModelRegistryEntry:
        for entry in self.list_entries():
            if (
                entry.model_name == model_name
                and entry.model_version == model_version
            ):
                return entry

        raise FileNotFoundError(
            f"Registry entry not found: {model_name} {model_version}"
        )

    def update_status(
        self,
        model_name: str,
        model_version: str,
        status: str,
        inference_tested: bool = False,
    ) -> ModelRegistryEntry:
        self._validate_status(status)
        if status == "production" and not inference_tested:
            raise ValueError(
                "Production status requires successful inference testing."
            )

        entries = list(self.list_entries())
        for index, entry in enumerate(entries):
            if (
                entry.model_name == model_name
                and entry.model_version == model_version
            ):
                updated_entry = ModelRegistryEntry(
                    model_name=entry.model_name,
                    model_version=entry.model_version,
                    artifact_location=entry.artifact_location,
                    status=status,
                    metrics=entry.metrics,
                    created_timestamp=entry.created_timestamp,
                )
                entries[index] = updated_entry
                self._write_entries(entries)
                return updated_entry

        raise FileNotFoundError(
            f"Registry entry not found: {model_name} {model_version}"
        )

    def version_state(self, model_name: str) -> dict[str, str | None]:
        """Expose production/candidate/rollback versions without loading artifacts."""
        entries = [entry for entry in self.list_entries() if entry.model_name == model_name]
        return {
            "current_production_version": next((e.model_version for e in entries if e.status == "production"), None),
            "candidate_version": next((e.model_version for e in entries if e.status == "candidate"), None),
            "previous_version": next((e.model_version for e in entries if e.status == "previous"), None),
        }

    def promote_candidate(
        self, model_name: str, model_version: str, *, approved: bool, inference_tested: bool
    ) -> ModelRegistryEntry:
        """Explicit promotion only; production artifacts are never overwritten."""
        if not approved:
            raise ValueError("Candidate promotion requires explicit approval.")
        if not inference_tested:
            raise ValueError("Candidate promotion requires successful inference testing.")
        candidate = self.get_entry(model_name, model_version)
        if candidate.status not in {"candidate", "validated", "previous"}:
            raise ValueError("Only a candidate, validated, or previous model can be promoted.")
        entries = list(self.list_entries())
        updated = []
        for entry in entries:
            status = entry.status
            if entry.model_name == model_name and entry.status == "production":
                status = "previous"
            if entry.model_name == model_name and entry.model_version == model_version:
                status = "production"
            updated.append(ModelRegistryEntry(entry.model_name, entry.model_version,
                           entry.artifact_location, status, entry.metrics, entry.created_timestamp))
        self._write_entries(updated)
        return self.get_entry(model_name, model_version)

    def rollback(self, model_name: str, previous_version: str, *, approved: bool,
                 inference_tested: bool) -> ModelRegistryEntry:
        """Make a retained previous artifact production after explicit approval."""
        return self.promote_candidate(model_name, previous_version, approved=approved,
                                      inference_tested=inference_tested)

    def list_entries(self) -> tuple[ModelRegistryEntry, ...]:
        if not self.registry_path.exists():
            return ()

        try:
            payload = json.loads(
                self.registry_path.read_text(encoding="utf-8")
            )
            return tuple(ModelRegistryEntry(**entry) for entry in payload)
        except (OSError, TypeError, ValueError, KeyError) as error:
            raise ValueError("Model registry is not readable.") from error

    def _write_entries(
        self,
        entries: list[ModelRegistryEntry],
    ) -> None:
        self.artifacts_directory.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(
            json.dumps([asdict(entry) for entry in entries], indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _validate_status(status: str) -> None:
        if status not in VALID_MODEL_STATUSES:
            raise ValueError(
                f"Invalid model status: {status}."
            )
