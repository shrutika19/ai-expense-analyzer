from pathlib import Path
import re


EXPENSE_CATEGORY_MODEL_NAME = "expense_category"
SEMANTIC_VERSION_PATTERN = re.compile(r"^v\d+\.\d+\.\d+$")


def get_bundle_directory(
    artifacts_directory: Path,
    model_name: str,
    model_version: str,
) -> Path:
    if model_name != EXPENSE_CATEGORY_MODEL_NAME:
        raise ValueError(
            "Published model name must be 'expense_category'."
        )
    if not SEMANTIC_VERSION_PATTERN.fullmatch(model_version):
        raise ValueError(
            "Model version must use semantic versioning: vX.Y.Z."
        )

    return artifacts_directory / model_name / model_version