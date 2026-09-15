from pathlib import Path

import joblib


class ModelStorage:

    def __init__(
        self,
        directory: str = "artifacts/models",
    ) -> None:
        self.directory = Path(directory)

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        model,
        filename: str,
    ) -> Path:

        path = self.directory / filename

        joblib.dump(
            model,
            path,
        )

        return path

    def load(
        self,
        filename: str,
    ):
        path = self.directory / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Model not found: {path}"
            )

        return joblib.load(path)