from dataclasses import dataclass

import pandas as pd
from scipy.sparse import csr_matrix, hstack

from expense_analyzer.ml.features.numerical_features import (
    AmountFeatureTransformer,
)
from expense_analyzer.ml.features.text_features import (
    TfidfFeatureExtractor,
    TfidfFeatureMetadata,
)


@dataclass(frozen=True)
class FeatureMetadata:
    tfidf: TfidfFeatureMetadata
    include_amount: bool
    numerical_features: tuple[str, ...]


@dataclass(frozen=True)
class FeatureMatrices:
    X_train: csr_matrix
    X_test: csr_matrix


class FeaturePipeline:
    DESCRIPTION_COLUMN = "description"
    AMOUNT_COLUMN = "amount"

    def __init__(
        self,
        text_extractor: TfidfFeatureExtractor | None = None,
        amount_transformer: AmountFeatureTransformer | None = None,
        include_amount: bool = True,
    ) -> None:
        self.text_extractor = (
            text_extractor or TfidfFeatureExtractor()
        )

        self.amount_transformer = (
            amount_transformer or AmountFeatureTransformer()
        )

        self.include_amount = include_amount

    def fit_transform(
        self,
        X_train: pd.DataFrame,
    ) -> csr_matrix:
        self._validate_columns(X_train)

        text_features = self.text_extractor.fit_transform(
            X_train[self.DESCRIPTION_COLUMN].tolist()
        )

        if not self.include_amount:
            return text_features.tocsr()

        amount_features = self.amount_transformer.transform(
            X_train[self.AMOUNT_COLUMN]
        )

        return hstack(
            [
                text_features,
                csr_matrix(amount_features),
            ],
            format="csr",
        )

    def transform(
        self,
        X_test: pd.DataFrame,
    ) -> csr_matrix:
        self._validate_columns(X_test)

        text_features = self.text_extractor.transform(
            X_test[self.DESCRIPTION_COLUMN].tolist()
        )

        if not self.include_amount:
            return text_features.tocsr()

        amount_features = self.amount_transformer.transform(
            X_test[self.AMOUNT_COLUMN]
        )

        return hstack(
            [
                text_features,
                csr_matrix(amount_features),
            ],
            format="csr",
        )

    def fit_transform_train_test(
        self,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
    ) -> FeatureMatrices:
        X_train_features = self.fit_transform(X_train)
        X_test_features = self.transform(X_test)

        return FeatureMatrices(
            X_train=X_train_features,
            X_test=X_test_features,
        )

    def get_metadata(self) -> FeatureMetadata:
        return FeatureMetadata(
            tfidf=self.text_extractor.get_metadata(),
            include_amount=self.include_amount,
            numerical_features=(
                (self.AMOUNT_COLUMN,)
                if self.include_amount
                else ()
            ),
        )

    def _validate_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        required_columns = {
            self.DESCRIPTION_COLUMN,
            self.AMOUNT_COLUMN,
        }

        missing_columns = required_columns - set(
            dataframe.columns
        )

        if missing_columns:
            raise ValueError(
                "Missing required feature columns: "
                f"{sorted(missing_columns)}"
            )