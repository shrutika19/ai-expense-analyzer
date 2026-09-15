import pandas as pd

from expense_analyzer.ml.training.configuration import (
    TrainingConfiguration,
)
from expense_analyzer.ml.training.trainer import (
    CategoryModelTrainer,
)


def train_model_a(
    X_train: pd.DataFrame,
    y_train: pd.Series,
):
    """
    Train baseline Model A.

    Features:
        description → TF-IDF

    Model:
        Logistic Regression
    """

    configuration = TrainingConfiguration(
        include_amount=False,
    )

    trainer = CategoryModelTrainer(
        configuration=configuration,
    )

    trained_model = trainer.train(
        X_train=X_train,
        y_train=y_train,
    )

    metadata = trained_model.feature_pipeline.get_metadata()

    benchmark = {
        "model": "Model A",
        "training_sample_count": len(X_train),
        "number_of_categories": y_train.nunique(),
        "tfidf_vocabulary_size": len(
            metadata.tfidf.vocabulary
        ),
        "model_configuration": {
            "max_iterations": (
                configuration.model.max_iterations
            ),
            "random_state": (
                configuration.model.random_state
            ),
        },
        "tfidf_configuration": {
            "lowercase": configuration.tfidf.lowercase,
            "ngram_range": configuration.tfidf.ngram_range,
            "min_df": configuration.tfidf.min_df,
            "max_features": configuration.tfidf.max_features,
        },
        "amount_included": configuration.include_amount,
    }

    return trained_model, benchmark


def train_model_b(
    X_train: pd.DataFrame,
    y_train: pd.Series,
):
    """
    Train baseline Model B.

    Features:
        description → TF-IDF
        amount      → numerical feature

    Model:
        Logistic Regression
    """

    configuration = TrainingConfiguration(
        include_amount=True,
    )

    trainer = CategoryModelTrainer(
        configuration=configuration,
    )

    trained_model = trainer.train(
        X_train=X_train,
        y_train=y_train,
    )

    metadata = trained_model.feature_pipeline.get_metadata()

    benchmark = {
        "model": "Model B",
        "training_sample_count": len(X_train),
        "number_of_categories": y_train.nunique(),
        "tfidf_vocabulary_size": len(
            metadata.tfidf.vocabulary
        ),
        "model_configuration": {
            "max_iterations": (
                configuration.model.max_iterations
            ),
            "random_state": (
                configuration.model.random_state
            ),
        },
        "tfidf_configuration": {
            "lowercase": configuration.tfidf.lowercase,
            "ngram_range": configuration.tfidf.ngram_range,
            "min_df": configuration.tfidf.min_df,
            "max_features": configuration.tfidf.max_features,
        },
        "amount_included": configuration.include_amount,
    }

    return trained_model, benchmark