from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)

from expense_analyzer.ml.evaluation.result import (
    PerCategoryMetrics,
)


def calculate_accuracy(
    y_true,
    y_pred,
) -> float:
    """Calculate classification accuracy."""

    return float(
        accuracy_score(
            y_true,
            y_pred,
        )
    )


def calculate_macro_precision(
    y_true,
    y_pred,
) -> float:
    """Calculate macro-averaged precision."""

    return float(
        precision_score(
            y_true,
            y_pred,
            average="macro",
            zero_division=0,
        )
    )


def calculate_macro_recall(
    y_true,
    y_pred,
) -> float:
    """Calculate macro-averaged recall."""

    return float(
        recall_score(
            y_true,
            y_pred,
            average="macro",
            zero_division=0,
        )
    )


def calculate_macro_f1(
    y_true,
    y_pred,
) -> float:
    """Calculate macro-averaged F1 score."""

    return float(
        f1_score(
            y_true,
            y_pred,
            average="macro",
            zero_division=0,
        )
    )


def calculate_weighted_precision(
    y_true,
    y_pred,
) -> float:
    """Calculate weighted precision."""

    return float(
        precision_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        )
    )


def calculate_weighted_recall(
    y_true,
    y_pred,
) -> float:
    """Calculate weighted recall."""

    return float(
        recall_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        )
    )


def calculate_weighted_f1(
    y_true,
    y_pred,
) -> float:
    """Calculate weighted F1 score."""

    return float(
        f1_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        )
    )


def calculate_per_category_metrics(
    y_true,
    y_pred,
    labels: list[str],
) -> tuple[PerCategoryMetrics, ...]:
    """Calculate precision, recall and F1 for every category."""

    precision = precision_score(
        y_true,
        y_pred,
        labels=labels,
        average=None,
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        y_pred,
        labels=labels,
        average=None,
        zero_division=0,
    )

    f1 = f1_score(
        y_true,
        y_pred,
        labels=labels,
        average=None,
        zero_division=0,
    )

    return tuple(
        PerCategoryMetrics(
            category=category,
            precision=float(category_precision),
            recall=float(category_recall),
            f1=float(category_f1),
        )
        for category, category_precision, category_recall, category_f1
        in zip(
            labels,
            precision,
            recall,
            f1,
        )
    )


def calculate_confusion_matrix(
    y_true,
    y_pred,
    labels: list[str],
) -> tuple[tuple[int, ...], ...]:
    """Calculate confusion matrix using a fixed category order."""

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    return tuple(
        tuple(int(value) for value in row)
        for row in matrix
    )