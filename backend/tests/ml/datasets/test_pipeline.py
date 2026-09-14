from datetime import date
from decimal import Decimal

import pandas as pd

from expense_analyzer.ml.datasets.cleaner import DatasetCleaningResult
from expense_analyzer.ml.datasets.pipeline import DatasetPreparationPipeline
from expense_analyzer.ml.datasets.splitter import DatasetSplitter


VALID_CATEGORIES = [
    "FOOD",
    "TRANSPORT",
    "SHOPPING",
    "ENTERTAINMENT",
]


def create_raw_dataframe() -> pd.DataFrame:
    records = []

    for category in VALID_CATEGORIES:
        for index in range(10):
            records.append(
                {
                    "description": f"{category} expense {index}",
                    "amount": Decimal("100.00"),
                    "category": category,
                    "expense_date": date(2026, 9, index + 1),
                }
            )

    # Invalid records that should be removed by the cleaner.
    records.extend(
        [
            {
                "description": None,
                "amount": Decimal("500.00"),
                "category": "FOOD",
                "expense_date": date(2026, 9, 20),
            },
            {
                "description": "",
                "amount": Decimal("500.00"),
                "category": "FOOD",
                "expense_date": date(2026, 9, 21),
            },
            {
                "description": "Invalid amount",
                "amount": Decimal("-100.00"),
                "category": "FOOD",
                "expense_date": date(2026, 9, 22),
            },
            {
                "description": "Missing category",
                "amount": Decimal("100.00"),
                "category": None,
                "expense_date": date(2026, 9, 23),
            },
        ]
    )

    return pd.DataFrame(records)


class MockLoader:
    def load(self) -> pd.DataFrame:
        return create_raw_dataframe()


class MockInspector:
    def inspect(self, dataframe: pd.DataFrame) -> None:
        return None


class MockCleaner:
    def clean(
        self,
        dataframe: pd.DataFrame,
    ) -> DatasetCleaningResult:
        cleaned = dataframe.copy()

        cleaned["description"] = (
            cleaned["description"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        cleaned = cleaned[
            (cleaned["description"] != "")
            & cleaned["category"].notna()
            & (cleaned["amount"] > 0)
        ].copy()

        return DatasetCleaningResult(
            dataframe=cleaned.reset_index(drop=True),
            removed_count=len(dataframe) - len(cleaned),
            unknown_categories=(),
        )


class MockSplitter(DatasetSplitter):
    pass


def create_pipeline() -> DatasetPreparationPipeline:
    return DatasetPreparationPipeline(
        loader=MockLoader(),
        inspector=MockInspector(),
        cleaner=MockCleaner(),
        splitter=MockSplitter(),
    )


def test_invalid_records_do_not_reach_training_data():
    pipeline = create_pipeline()

    prepared = pipeline.prepare()

    combined_data = pd.concat(
        [
            prepared.X_train,
            prepared.X_test,
        ],
        ignore_index=True,
    )

    assert not combined_data["description"].isna().any()
    assert not combined_data["description"].eq("").any()
    assert not (combined_data["description"].str.strip() == "").any()
    assert not combined_data["amount"].isna().any()
    assert not (combined_data["amount"] <= 0).any()


def test_target_exists():
    pipeline = create_pipeline()

    prepared = pipeline.prepare()

    assert prepared.y_train is not None
    assert prepared.y_test is not None


def test_no_missing_target_values():
    pipeline = create_pipeline()

    prepared = pipeline.prepare()

    assert not prepared.y_train.isna().any()
    assert not prepared.y_test.isna().any()


def test_train_and_test_contain_valid_categories():
    pipeline = create_pipeline()

    prepared = pipeline.prepare()

    assert set(prepared.y_train).issubset(
        set(VALID_CATEGORIES)
    )

    assert set(prepared.y_test).issubset(
        set(VALID_CATEGORIES)
    )


def test_target_is_not_present_in_features():
    pipeline = create_pipeline()

    prepared = pipeline.prepare()

    assert "category" not in prepared.X_train.columns
    assert "category" not in prepared.X_test.columns


def test_train_and_test_contain_valid_records():
    pipeline = create_pipeline()

    prepared = pipeline.prepare()

    assert len(prepared.X_train) > 0
    assert len(prepared.X_test) > 0

    assert len(prepared.X_train) == len(prepared.y_train)
    assert len(prepared.X_test) == len(prepared.y_test)


def test_split_is_reproducible():
    pipeline_1 = create_pipeline()
    pipeline_2 = create_pipeline()

    prepared_1 = pipeline_1.prepare()
    prepared_2 = pipeline_2.prepare()

    pd.testing.assert_frame_equal(
        prepared_1.X_train,
        prepared_2.X_train,
    )

    pd.testing.assert_frame_equal(
        prepared_1.X_test,
        prepared_2.X_test,
    )

    pd.testing.assert_series_equal(
        prepared_1.y_train,
        prepared_2.y_train,
    )

    pd.testing.assert_series_equal(
        prepared_1.y_test,
        prepared_2.y_test,
    )