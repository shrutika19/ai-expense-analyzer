from dataclasses import dataclass

import pandas as pd

from expense_analyzer.ml.datasets.pipeline import (
    DatasetPreparationPipeline,
    PreparedDataset,
)
from expense_analyzer.ml.training.train_baseline import (
    train_model_a,
)


MANUAL_DESCRIPTIONS = (
    "Uber ride to office",
    "Restaurant dinner",
    "Amazon household purchase",
    "Netflix subscription",
    "Electricity bill",
)


@dataclass(frozen=True)
class ManualPrediction:
    description: str
    predicted_category: str
    confidence: float


def run_manual_prediction_check(
    dataset: PreparedDataset,
) -> tuple[ManualPrediction, ...]:
    """Train Model A in memory and return manual prediction checks."""

    trained_model, _ = train_model_a(
        X_train=dataset.X_train,
        y_train=dataset.y_train,
        test_row_count=len(dataset.X_test),
    )

    examples = pd.DataFrame(
        {
            "description": MANUAL_DESCRIPTIONS,
            "amount": [100] * len(MANUAL_DESCRIPTIONS),
        }
    )

    feature_matrix = trained_model.feature_pipeline.transform(
        examples
    )
    categories = trained_model.classifier.predict(
        feature_matrix
    )
    probabilities = trained_model.classifier.predict_proba(
        feature_matrix
    )

    return tuple(
        ManualPrediction(
            description=description,
            predicted_category=category,
            confidence=float(max(probability_row)),
        )
        for description, category, probability_row in zip(
            MANUAL_DESCRIPTIONS,
            categories,
            probabilities,
        )
    )


def print_manual_prediction_check(
    predictions: tuple[ManualPrediction, ...],
) -> None:
    print(
        f"{'Description':<30}"
        f"{'Predicted category':<20}"
        "Confidence"
    )

    for prediction in predictions:
        print(
            f"{prediction.description:<30}"
            f"{prediction.predicted_category:<20}"
            f"{prediction.confidence:.4f}"
        )


def main() -> None:
    dataset = DatasetPreparationPipeline().prepare()
    predictions = run_manual_prediction_check(dataset)
    print_manual_prediction_check(predictions)


if __name__ == "__main__":
    main()