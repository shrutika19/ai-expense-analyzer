from expense_analyzer.ml.models.registry import ModelRegistry, ModelRegistryEntry


def entry(version: str, status: str) -> ModelRegistryEntry:
    return ModelRegistryEntry("expense_category", version, f"/models/{version}",
                              status, {"macro_f1": 0.8}, "2026-09-25T00:00:00Z")


def test_promote_keeps_previous_artifact_available_for_rollback(tmp_path):
    registry = ModelRegistry(tmp_path)
    registry._write_entries([entry("v1.0.0", "production"), entry("v1.1.0", "candidate")])

    registry.promote_candidate("expense_category", "v1.1.0", approved=True, inference_tested=True)

    assert registry.version_state("expense_category") == {
        "current_production_version": "v1.1.0", "candidate_version": None,
        "previous_version": "v1.0.0",
    }
    registry.rollback("expense_category", "v1.0.0", approved=True, inference_tested=True)
    assert registry.version_state("expense_category")["current_production_version"] == "v1.0.0"
