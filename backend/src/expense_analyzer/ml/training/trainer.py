from dataclasses import dataclass

import pandas as pd
from sklearn.linear_model import LogisticRegression

from expense_analyzer.domain.enums.expense_category import (
    ExpenseCategory,
)
from expense_analyzer.ml.features.feature_pipeline import (
    FeaturePipeline,
)
from expense_analyzer.ml.features.text_features import (
    TfidfFeatureExtractor,
)
from expense_analyzer.ml.training.configuration import (
    TrainingConfiguration,
)


@dataclass(frozen=True)
class TrainedModel:
    classifier: LogisticRegression
    feature_pipeline: FeaturePipeline


class CategoryModelTrainer:
    """
    Responsible only for training the expense category model.

    Training flow:

        X_train + y_train
              ↓
        Feature Pipeline
              ↓
        Feature Matrix
              ↓
        Logistic Regression
              ↓
        TrainedModel

    Prediction/inference does not belong here.
    """

    CATEGORY_COLUMN = "category"

    def __init__(
        self,
        configuration: TrainingConfiguration | None = None,
    ) -> None:
        self.configuration = (
            configuration or TrainingConfiguration()
        )

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        feature_pipeline: FeaturePipeline | None = None,
    ) -> TrainedModel:
        """
        Validate training data, fit the feature pipeline using
        training data only, and train Logistic Regression.
        """

        self._validate_training_data(
            X_train=X_train,
            y_train=y_train,
        )

        pipeline = (
            feature_pipeline
            or self._create_feature_pipeline()
        )

        # Fit feature pipeline ONLY on training data.
        X_train_features = pipeline.fit_transform(
            X_train
        )

        classifier = LogisticRegression(
            max_iter=(
                self.configuration
                .model
                .max_iterations
            ),
            random_state=(
                self.configuration
                .model
                .random_state
            ),
        )

        classifier.fit(
            X_train_features,
            y_train,
        )

        return TrainedModel(
            classifier=classifier,
            feature_pipeline=pipeline,
        )

    def _create_feature_pipeline(
        self,
    ) -> FeaturePipeline:
        tfidf_configuration = self.configuration.tfidf

        return FeaturePipeline(
            text_extractor=TfidfFeatureExtractor(
                lowercase=tfidf_configuration.lowercase,
                ngram_range=tfidf_configuration.ngram_range,
                min_df=tfidf_configuration.min_df,
                max_features=tfidf_configuration.max_features,
            ),
            include_amount=(
                self.configuration.include_amount
            ),
        )

    def _validate_training_data(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
    ) -> None:
        if X_train.empty:
            raise ValueError(
                "Training data cannot be empty."
            )

        if y_train.empty:
            raise ValueError(
                "Training target cannot be empty."
            )

        if len(X_train) != len(y_train):
            raise ValueError(
                "Training features and target must have "
                "the same number of rows."
            )

        if y_train.name != self.CATEGORY_COLUMN:
            raise ValueError(
                "Training target must be the "
                f"'{self.CATEGORY_COLUMN}' column."
            )

        if y_train.isna().any():
            raise ValueError(
                "Training target cannot contain missing values."
            )

        categories = set(
            y_train.astype(str)
        )

        if len(categories) < 2:
            raise ValueError(
                "Training data must contain at least "
                "2 categories."
            )

        supported_categories = {
            category.value
            for category in ExpenseCategory
        }

        unknown_categories = (
            categories - supported_categories
        )

        if unknown_categories:
            raise ValueError(
                "Unknown expense categories found: "
                f"{sorted(unknown_categories)}"
            )