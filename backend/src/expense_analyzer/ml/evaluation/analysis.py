import math

from expense_analyzer.ml.evaluation.result import (
    ConfidenceSummary,
    ConfusionPair,
    EvaluatedPrediction,
)


CONFIDENCE_BANDS = (
    ("0.90-1.00", 0.90),
    ("0.80-0.89", 0.80),
    ("0.70-0.79", 0.70),
    ("0.60-0.69", 0.60),
    ("<0.60", 0.00),
)


def validate_probabilities(probabilities) -> None:
    for probability_row in probabilities:
        if any(
            not math.isfinite(float(value))
            or not 0.0 <= float(value) <= 1.0
            for value in probability_row
        ):
            raise ValueError("Prediction probabilities must be in [0, 1].")

        if not math.isclose(
            sum(float(value) for value in probability_row),
            1.0,
            abs_tol=1e-9,
        ):
            raise ValueError("Prediction probabilities must sum to 1.")


def create_evaluated_predictions(
    descriptions: list[str],
    y_true,
    y_pred,
    probabilities,
) -> tuple[EvaluatedPrediction, ...]:
    return tuple(
        EvaluatedPrediction(
            description=description,
            actual_category=actual_category,
            predicted_category=predicted_category,
            confidence=max(float(value) for value in probability_row),
            correct=actual_category == predicted_category,
        )
        for description, actual_category, predicted_category, probability_row
        in zip(descriptions, y_true, y_pred, probabilities)
    )


def summarize_confidence(
    predictions: tuple[EvaluatedPrediction, ...],
) -> ConfidenceSummary:
    correct_confidences = [
        prediction.confidence
        for prediction in predictions
        if prediction.correct
    ]
    incorrect_confidences = [
        prediction.confidence
        for prediction in predictions
        if not prediction.correct
    ]

    band_counts = []
    for name, minimum in CONFIDENCE_BANDS:
        if minimum == 0.0:
            count = sum(prediction.confidence < 0.60 for prediction in predictions)
        else:
            count = sum(
                minimum <= prediction.confidence < minimum + 0.10
                for prediction in predictions
            )
        band_counts.append((name, count))

    return ConfidenceSummary(
        correct_mean=(
            sum(correct_confidences) / len(correct_confidences)
            if correct_confidences
            else None
        ),
        incorrect_mean=(
            sum(incorrect_confidences) / len(incorrect_confidences)
            if incorrect_confidences
            else None
        ),
        bands=tuple(band_counts),
    )


def find_top_confusions(
    confusion_matrix: tuple[tuple[int, ...], ...],
    labels: tuple[str, ...],
) -> tuple[ConfusionPair, ...]:
    pairs = []
    for actual_index, actual_category in enumerate(labels):
        for predicted_index, predicted_category in enumerate(labels):
            if actual_index == predicted_index:
                continue

            count = confusion_matrix[actual_index][predicted_index]
            if count:
                pairs.append(
                    ConfusionPair(
                        actual_category=actual_category,
                        predicted_category=predicted_category,
                        count=count,
                    )
                )

    return tuple(sorted(pairs, key=lambda pair: pair.count, reverse=True))