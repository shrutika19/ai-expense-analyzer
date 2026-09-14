import pandas as pd

from expense_analyzer.ml.datasets.models import (
    AmountStatistics,
    CategoryStatistics,
    DatasetStatistics,
    MissingValueStatistics,
)


class DatasetInspector:
    """Inspects an expense dataset without modifying it."""

    REQUIRED_COLUMNS = {
        "description",
        "amount",
        "category",
    }

    def inspect(self, dataframe: pd.DataFrame) -> DatasetStatistics:
        self._validate_columns(dataframe)

        return DatasetStatistics(
            row_count=len(dataframe),
            column_count=len(dataframe.columns),
            columns=self._schema(dataframe),
            missing_values=self._missing_values(dataframe),
            category_distribution=self._categories(dataframe),
            duplicate_count=self._duplicate_records(dataframe),
            amount_statistics=self._amount_statistics(dataframe),
        )

    def _validate_columns(self, dataframe: pd.DataFrame) -> None:
        missing_columns = self.REQUIRED_COLUMNS - set(dataframe.columns)

        if missing_columns:
            raise ValueError(
                f"Dataset is missing required columns: {missing_columns}"
            )

    def _schema(self, dataframe: pd.DataFrame) -> dict[str, str]:
        return {
            column: str(dataframe[column].dtype)
            for column in dataframe.columns
        }

    def _missing_values(
        self,
        dataframe: pd.DataFrame,
    ) -> dict[str, MissingValueStatistics]:
        result: dict[str, MissingValueStatistics] = {}

        for column in ("description", "amount", "category"):
            missing_count = int(dataframe[column].isna().sum())

            missing_percentage = (
                missing_count / len(dataframe) * 100
                if len(dataframe) > 0
                else 0.0
            )

            result[column] = MissingValueStatistics(
                missing_count=missing_count,
                missing_percentage=missing_percentage,
            )

        return result

    def _categories(
        self,
        dataframe: pd.DataFrame,
    ) -> dict[str, CategoryStatistics]:
        category_counts = dataframe["category"].value_counts()
        total_records = len(dataframe)

        return {
            str(category): CategoryStatistics(
                record_count=int(count),
                percentage=(
                    count / total_records * 100
                    if total_records > 0
                    else 0.0
                ),
            )
            for category, count in category_counts.items()
        }

    def _duplicate_records(self, dataframe: pd.DataFrame) -> int:
        return int(dataframe.duplicated().sum())

    def _amount_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> AmountStatistics:
        return AmountStatistics(
            min=float(dataframe["amount"].min()),
            max=float(dataframe["amount"].max()),
            mean=float(dataframe["amount"].mean()),
        )