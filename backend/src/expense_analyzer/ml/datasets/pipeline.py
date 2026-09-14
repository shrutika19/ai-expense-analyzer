from dataclasses import dataclass

import pandas as pd

from expense_analyzer.ml.datasets.cleaner import DatasetCleaner
from expense_analyzer.ml.datasets.inspector import DatasetInspector
from expense_analyzer.ml.datasets.loader import DatasetLoader
from expense_analyzer.ml.datasets.splitter import DatasetSplitter


@dataclass(frozen=True)
class PreparedDataset:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series


class DatasetPreparationPipeline:
    """Orchestrates expense dataset preparation for ML training."""

    TARGET_COLUMN = "category"

    def __init__(
        self,
        loader: DatasetLoader | None = None,
        inspector: DatasetInspector | None = None,
        cleaner: DatasetCleaner | None = None,
        splitter: DatasetSplitter | None = None,
    ) -> None:
        self.loader = loader or DatasetLoader()
        self.inspector = inspector or DatasetInspector()
        self.cleaner = cleaner or DatasetCleaner()
        self.splitter = splitter or DatasetSplitter()

    def prepare(self) -> PreparedDataset:
        # 1. Load raw data.
        dataframe = self.loader.load()

        # 2. Inspect raw dataset.
        self.inspector.inspect(dataframe)

        # 3. Clean dataset.
        cleaning_result = self.cleaner.clean(dataframe)
        cleaned_dataframe = cleaning_result.dataframe

        # 4. Inspect cleaned dataset.
        self.inspector.inspect(cleaned_dataframe)

        # 5. Split cleaned dataset into train/test.
        train_data, test_data = self.splitter.split(
            cleaned_dataframe
        )

        # 6. Separate features and target.
        X_train = train_data.drop(columns=[self.TARGET_COLUMN])
        X_test = test_data.drop(columns=[self.TARGET_COLUMN])

        y_train = train_data[self.TARGET_COLUMN]
        y_test = test_data[self.TARGET_COLUMN]

        return PreparedDataset(
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
        )