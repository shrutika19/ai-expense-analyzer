from datetime import date
from decimal import Decimal
from uuid import uuid4

from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.domain.enums.category_source import CategorySource
from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.ml.feedback.service import FeedbackService


class FeedbackRepository:
    def __init__(self, records):
        self.records = records

    def find_feedback_records(self, user_id):
        return self.records

    def find_prediction_records(self, user_id):
        return self.records


def feedback(actual, predicted, confidence=0.9):
    return Expense(
        user_id=uuid4(), amount=Decimal("120.00"), description="Coffee",
        category=actual, predicted_category=predicted,
        category_source=CategorySource.MANUAL,
        category_confidence=confidence, model_version="v1.0.0",
        expense_date=date(2026, 9, 25),
    )


def test_dataset_excludes_duplicates_and_performance_compares_final_category():
    records = [
        feedback(ExpenseCategory.FOOD, ExpenseCategory.FOOD),
        feedback(ExpenseCategory.FOOD, ExpenseCategory.FOOD),
        feedback(ExpenseCategory.TRAVEL, ExpenseCategory.TRANSPORT, 0.4),
    ]
    service = FeedbackService(FeedbackRepository(records), 0.7)

    dataset = service.dataset(uuid4())
    report = service.performance(uuid4())

    assert len(dataset) == 2
    assert set(dataset[0].__dict__) == {
        "description", "amount", "predicted_category", "actual_category",
        "model_version", "confidence", "expense_date",
    }
    assert report["sample_size"] == 2
    assert report["accuracy"] == 0.5
    assert report["manual_correction_rate"] == 0.5
    assert report["low_confidence_prediction_rate"] == 0.5


def test_monitoring_and_diagnostics_report_corrections_and_confusions():
    records = [
        feedback(ExpenseCategory.FOOD, ExpenseCategory.FOOD),
        feedback(ExpenseCategory.TRAVEL, ExpenseCategory.TRANSPORT, 0.9),
    ]
    service = FeedbackService(FeedbackRepository(records), 0.7)

    monitoring = service.monitoring(uuid4())
    diagnostics = service.diagnose(uuid4())

    assert monitoring["total_predictions"] == 2
    assert monitoring["manual_correction_percentage"] == 0.5
    assert monitoring["predictions_by_category"]["Transport"] == 1
    assert diagnostics["frequent_confusions"] == [{
        "actual_category": "Travel", "predicted_category": "Transport", "count": 1,
    }]
    assert len(diagnostics["high_confidence_incorrect_predictions"]) == 1


def test_dataset_excludes_invalid_feedback():
    invalid = feedback(ExpenseCategory.FOOD, ExpenseCategory.FOOD)
    invalid.category_confidence = 1.5
    service = FeedbackService(FeedbackRepository([invalid]), 0.7)

    assert service.dataset(uuid4()) == []
