from dataclasses import dataclass

import pandas as pd

from expense_analyzer.ml.datasets.cleaner import DatasetCleaner
from expense_analyzer.ml.datasets.pipeline import PreparedDataset
from expense_analyzer.ml.datasets.splitter import DatasetSplitter
from expense_analyzer.ml.feedback.service import FeedbackRecord


@dataclass(frozen=True)
class RetrainingRules:
    minimum_new_labels: int = 50
    correction_rate_threshold: float = 0.15
    distribution_change_threshold: float = 0.20


class ControlledRetrainingWorkflow:
    """Database feedback -> clean -> split. Training and deployment stay explicit."""

    def __init__(self, rules: RetrainingRules | None = None) -> None:
        self.rules = rules or RetrainingRules()
        self.cleaner = DatasetCleaner()
        self.splitter = DatasetSplitter()

    def assess_eligibility(self, *, new_labeled_count: int, correction_rate: float,
                            distribution_change: float, new_category: bool,
                            scheduled_review_due: bool) -> dict:
        reasons = []
        if new_labeled_count >= self.rules.minimum_new_labels:
            reasons.append("sufficient_new_labeled_expenses")
        if correction_rate >= self.rules.correction_rate_threshold:
            reasons.append("significant_manual_correction_rate")
        if distribution_change >= self.rules.distribution_change_threshold:
            reasons.append("category_distribution_change")
        if new_category:
            reasons.append("new_category_introduced")
        if scheduled_review_due:
            reasons.append("scheduled_model_review")
        return {"retraining_allowed": bool(reasons), "reasons": reasons,
                "automatic_deployment": False}

    def prepare(self, feedback: list[FeedbackRecord]) -> PreparedDataset:
        """Reusable clean/split stage; callers then use existing features/train/evaluate/compare modules."""
        raw = pd.DataFrame([{
            "description": record.description, "amount": record.amount,
            "category": record.actual_category, "expense_date": record.expense_date,
        } for record in feedback])
        if raw.empty:
            raise ValueError("No validated feedback is available for retraining.")
        cleaned = self.cleaner.clean(raw).dataframe
        train, test = self.splitter.split(cleaned)
        return PreparedDataset(
            X_train=train.drop(columns=["category"]), X_test=test.drop(columns=["category"]),
            y_train=train["category"], y_test=test["category"],
        )
