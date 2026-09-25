from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.ml.evaluation.metrics import (
    calculate_accuracy,
    calculate_macro_f1,
    calculate_macro_precision,
    calculate_macro_recall,
    calculate_per_category_metrics,
    calculate_confusion_matrix,
)
from expense_analyzer.repositories.expense_repository import ExpenseRepository


@dataclass(frozen=True)
class FeedbackRecord:
    description: str
    amount: Decimal
    predicted_category: str
    actual_category: str
    model_version: str
    confidence: float
    expense_date: date


class FeedbackService:
    """Build a clean, reviewable dataset; it never retrains or publishes a model."""

    def __init__(self, repository: ExpenseRepository, low_confidence_threshold: float | None) -> None:
        self.repository = repository
        self.low_confidence_threshold = low_confidence_threshold

    def dataset(self, user_id: UUID) -> list[FeedbackRecord]:
        # A normalized semantic key prevents repeat submissions from being
        # amplified during retraining. Latest database state is already final.
        unique: dict[tuple[str, str, str, str], FeedbackRecord] = {}
        for expense in self.repository.find_feedback_records(user_id):
            if not self._is_valid(expense):
                continue
            record = FeedbackRecord(
                description=expense.description.strip(),
                amount=expense.amount,
                predicted_category=expense.predicted_category.value,
                actual_category=expense.category.value,
                model_version=expense.model_version,
                confidence=expense.category_confidence,
                expense_date=expense.expense_date,
            )
            key = (record.description.casefold(), str(record.amount),
                   record.actual_category, record.model_version)
            unique[key] = record
        return list(unique.values())

    def performance(self, user_id: UUID) -> dict:
        records = self.dataset(user_id)
        if not records:
            return {"sample_size": 0, "accuracy": None, "precision": None,
                    "recall": None, "f1": None, "per_category": [],
                    "low_confidence_prediction_rate": None,
                    "manual_correction_rate": None}

        actual = [record.actual_category for record in records]
        predicted = [record.predicted_category for record in records]
        labels = [category.value for category in ExpenseCategory
                  if category.value in set(actual) | set(predicted)]
        low_count = sum(
            self.low_confidence_threshold is not None
            and record.confidence < self.low_confidence_threshold
            for record in records
        )
        corrected = sum(a != p for a, p in zip(actual, predicted))
        return {
            "sample_size": len(records),
            "accuracy": calculate_accuracy(actual, predicted),
            "precision": calculate_macro_precision(actual, predicted),
            "recall": calculate_macro_recall(actual, predicted),
            "f1": calculate_macro_f1(actual, predicted),
            "per_category": [asdict(metric) for metric in calculate_per_category_metrics(actual, predicted, labels)],
            "low_confidence_prediction_rate": low_count / len(records),
            "manual_correction_rate": corrected / len(records),
        }

    def monitoring(self, user_id: UUID) -> dict:
        """Operational statistics over every persisted prediction."""
        predictions = self.repository.find_prediction_records(user_id)
        if not predictions:
            return {"total_predictions": 0, "predictions_by_category": {},
                    "average_confidence": None, "low_confidence_percentage": None,
                    "manual_correction_percentage": None, "model_version_usage": {}}
        low = sum(self.low_confidence_threshold is not None and
                  expense.category_confidence < self.low_confidence_threshold
                  for expense in predictions)
        confirmed = [expense for expense in predictions
                     if expense.category_source.value == "manual"]
        corrections = sum(expense.category != expense.predicted_category
                          for expense in confirmed)
        return {
            "total_predictions": len(predictions),
            "predictions_by_category": dict(Counter(
                expense.predicted_category.value for expense in predictions)),
            "average_confidence": sum(expense.category_confidence for expense in predictions) / len(predictions),
            "low_confidence_percentage": low / len(predictions),
            "manual_correction_percentage": (corrections / len(confirmed)
                                             if confirmed else None),
            "model_version_usage": dict(Counter(
                expense.model_version for expense in predictions)),
        }

    def diagnose(self, user_id: UUID, poor_f1_threshold: float = 0.60) -> dict:
        """Pinpoint error patterns using only user-confirmed ground truth."""
        records = self.dataset(user_id)
        if not records:
            return {"frequent_confusions": [], "poor_f1_categories": [],
                    "high_confidence_incorrect_predictions": [],
                    "few_training_examples": [], "category_distribution_over_time": {}}
        actual = [record.actual_category for record in records]
        predicted = [record.predicted_category for record in records]
        labels = sorted(set(actual) | set(predicted))
        matrix = calculate_confusion_matrix(actual, predicted, labels)
        confusions = sorted(
            ({"actual_category": labels[row], "predicted_category": labels[column], "count": count}
             for row, values in enumerate(matrix) for column, count in enumerate(values)
             if row != column and count), key=lambda item: item["count"], reverse=True)
        per_category = calculate_per_category_metrics(actual, predicted, labels)
        counts = Counter(actual)
        distribution: dict[str, dict[str, int]] = {}
        for record in records:
            month = record.expense_date.strftime("%Y-%m")
            distribution.setdefault(month, {})[record.actual_category] = (
                distribution.setdefault(month, {}).get(record.actual_category, 0) + 1)
        return {
            "frequent_confusions": confusions,
            "poor_f1_categories": [asdict(metric) for metric in per_category
                                    if metric.f1 < poor_f1_threshold],
            "high_confidence_incorrect_predictions": [
                {"description": record.description, "predicted_category": record.predicted_category,
                 "actual_category": record.actual_category, "confidence": record.confidence}
                for record in records if record.actual_category != record.predicted_category
                and (self.low_confidence_threshold is None or record.confidence >= self.low_confidence_threshold)
            ],
            "few_training_examples": [
                {"category": category, "count": count} for category, count in counts.items() if count < 5],
            "category_distribution_over_time": distribution,
        }

    @staticmethod
    def _is_valid(expense: Expense) -> bool:
        return bool(
            expense.description.strip()
            and expense.amount > 0
            and expense.predicted_category is not None
            and expense.category is not None
            and expense.model_version
            and expense.category_confidence is not None
            and 0 <= expense.category_confidence <= 1
        )
