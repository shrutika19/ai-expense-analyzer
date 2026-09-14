import pandas as pd
from sklearn.model_selection import train_test_split


class DatasetSplitter:
    """Splits a cleaned expense dataset into stratified train and test sets."""

    TEST_SIZE = 0.20
    RANDOM_STATE = 42
    TARGET_COLUMN = "category"

    def split(
        self,
        dataframe: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        if self.TARGET_COLUMN not in dataframe.columns:
            raise ValueError(
                f"Dataset must contain '{self.TARGET_COLUMN}' column."
            )

        if dataframe.empty:
            raise ValueError("Cannot split an empty dataset.")

        train_data, test_data = train_test_split(
            dataframe,
            test_size=self.TEST_SIZE,
            random_state=self.RANDOM_STATE,
            stratify=dataframe[self.TARGET_COLUMN],
        )

        return (
            train_data.reset_index(drop=True),
            test_data.reset_index(drop=True),
        )