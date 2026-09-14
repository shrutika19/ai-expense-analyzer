from dataclasses import dataclass
from decimal import Decimal

import pandas as pd

from expense_analyzer.domain.enums.expense_category import ExpenseCategory


@dataclass(frozen=True)
class DatasetCleaningResult:
    dataframe: pd.DataFrame
    removed_count: int
    unknown_categories: tuple[str, ...]


class DatasetCleaner:
    """Cleans and validates an expense dataset."""

    DUPLICATE_COLUMNS = [
        "description",
        "amount",
        "category",
        "expense_date",
    ]

    def clean(self, dataframe: pd.DataFrame) -> DatasetCleaningResult:
        original_count = len(dataframe)

        cleaned = dataframe.copy()

        # Normalize description whitespace.
        cleaned["description"] = (
            cleaned["description"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # Remove unusable records.
        cleaned = self._remove_unusable_records(cleaned)

        # Validate categories.
        unknown_categories = self._find_unknown_categories(cleaned)

        if unknown_categories:
            raise ValueError(
                "Unknown expense categories found: "
                f"{sorted(unknown_categories)}"
            )

        # Remove exact ML duplicates.
        cleaned = self._remove_duplicates(cleaned)

        removed_count = original_count - len(cleaned)

        return DatasetCleaningResult(
            dataframe=cleaned.reset_index(drop=True),
            removed_count=removed_count,
            unknown_categories=tuple(),
        )

    def _remove_unusable_records(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        valid_description = dataframe["description"].ne("")

        valid_category = (
            dataframe["category"].notna()
            & dataframe["category"].astype(str).str.strip().ne("")
        )

        valid_amount = dataframe["amount"].apply(
            self._is_valid_amount
        )

        return dataframe[
            valid_description
            & valid_category
            & valid_amount
        ].copy()

    @staticmethod
    def _is_valid_amount(value: object) -> bool:
        if value is None or pd.isna(value):
            return False

        try:
            amount = Decimal(str(value))
        except Exception:
            return False

        return amount > Decimal("0")

    @staticmethod
    def _find_unknown_categories(
        dataframe: pd.DataFrame,
    ) -> set[str]:
        valid_categories = {
            category.value
            for category in ExpenseCategory
        }

        dataset_categories = {
            str(category).strip()
            for category in dataframe["category"].dropna()
        }

        return dataset_categories - valid_categories

    def _remove_duplicates(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        return dataframe.drop_duplicates(
            subset=self.DUPLICATE_COLUMNS,
            keep="first",
        )