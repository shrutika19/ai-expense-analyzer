from expense_analyzer.ml.evaluation.evaluator import (
    ModelEvaluator,
)
from expense_analyzer.ml.training.model_storage import (
    ModelStorage,
)


CATEGORIES = [
    "Food",
    "Transport",
    "Travel",
    "Shopping",
    "Entertainment",
    "Utilities",
    "Healthcare",
    "Education",
    "Rent",
    "Other",
]


def print_evaluation(result) -> None:
    """Print a complete model evaluation."""

    print()
    print(result.model_name)
    print("=" * 60)

    print(
        f"Accuracy:              "
        f"{result.accuracy:.4f}"
    )

    print(
        f"Precision (macro):     "
        f"{result.macro_precision:.4f}"
    )

    print(
        f"Precision (weighted):  "
        f"{result.weighted_precision:.4f}"
    )

    print(
        f"Recall (macro):        "
        f"{result.macro_recall:.4f}"
    )

    print(
        f"Recall (weighted):     "
        f"{result.weighted_recall:.4f}"
    )

    print(
        f"F1-score (macro):      "
        f"{result.macro_f1:.4f}"
    )

    print(
        f"F1-score (weighted):   "
        f"{result.weighted_f1:.4f}"
    )

    print()
    print(
        f"{result.model_name} - "
        "Per Category Evaluation"
    )

    print("=" * 70)

    print(
        f"{'Category':<20}"
        f"{'Precision':>12}"
        f"{'Recall':>12}"
        f"{'F1':>12}"
    )

    print("-" * 70)

    for metric in result.per_category_metrics:

        print(
            f"{metric.category:<20}"
            f"{metric.precision:>12.4f}"
            f"{metric.recall:>12.4f}"
            f"{metric.f1:>12.4f}"
        )

    print()
    print(
        f"{result.model_name} - "
        "Confusion Matrix"
    )

    print("=" * 100)

    print(
        f"{'Actual / Predicted':<20}"
        + "".join(
            f"{label[:10]:>12}"
            for label in result.labels
        )
    )

    print("-" * 100)

    for actual_label, row in zip(
        result.labels,
        result.confusion_matrix,
    ):
        print(
            f"{actual_label:<20}"
            + "".join(
                f"{value:>12}"
                for value in row
            )
        )

    print()
    print(
        f"{result.model_name} - "
        "Biggest Confusion Pairs"
    )

    print("=" * 60)

    confusion_pairs = []

    for actual_index, actual_label in enumerate(
        result.labels
    ):
        for predicted_index, predicted_label in enumerate(
            result.labels
        ):

            if actual_index == predicted_index:
                continue

            count = result.confusion_matrix[
                actual_index
            ][
                predicted_index
            ]

            if count > 0:
                confusion_pairs.append(
                    (
                        count,
                        actual_label,
                        predicted_label,
                    )
                )

    confusion_pairs.sort(
        reverse=True
    )

    if not confusion_pairs:
        print("No confusion pairs found.")
        return

    for count, actual, predicted in confusion_pairs:
        print(
            f"{actual} -> {predicted}: "
            f"{count} prediction(s)"
        )


def main() -> None:
    """Evaluate both baseline models."""

    # --------------------------------------------------
    # Step 5: Load trained models.
    # --------------------------------------------------

    storage = ModelStorage()

    model_a = storage.load(
        "model_a.joblib"
    )

    model_b = storage.load(
        "model_b.joblib"
    )

    # --------------------------------------------------
    # Load the SAME test dataset used for both models.
    #
    # Replace this import/call with your project's
    # existing dataset loader.
    # --------------------------------------------------

    from expense_analyzer.ml.data.loader import (
        load_dataset,
    )

    dataset = load_dataset()

    X_test = dataset.X_test
    y_test = dataset.y_test

    # --------------------------------------------------
    # Step 6 / Step 7: Evaluate models.
    # --------------------------------------------------

    evaluator = ModelEvaluator()

    result_a = evaluator.evaluate(
        model=model_a,
        model_name=(
            "MODEL A - TF-IDF + "
            "Logistic Regression"
        ),
        X_test=X_test,
        y_test=y_test,
        labels=CATEGORIES,
    )

    result_b = evaluator.evaluate(
        model=model_b,
        model_name=(
            "MODEL B - TF-IDF + Amount + "
            "Logistic Regression"
        ),
        X_test=X_test,
        y_test=y_test,
        labels=CATEGORIES,
    )

    # --------------------------------------------------
    # Display results.
    # --------------------------------------------------

    print_evaluation(result_a)
    print_evaluation(result_b)

    print()
    print("=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()