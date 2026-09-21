from dataclasses import dataclass
from pathlib import Path

from expense_analyzer.domain.enums.expense_category import (
    ExpenseCategory,
)
from expense_analyzer.ml.datasets.pipeline import (
    DatasetPreparationPipeline,
)
from expense_analyzer.ml.evaluation.acceptance import (
    AcceptanceAssessment,
    AcceptanceCriteria,
    assess_acceptance,
)
from expense_analyzer.ml.evaluation.comparison import ModelComparison
from expense_analyzer.ml.evaluation.evaluator import ModelEvaluator
from expense_analyzer.ml.evaluation.reporting import write_report
from expense_analyzer.ml.training.train_baseline import (
    train_model_a,
    train_model_b,
)


@dataclass(frozen=True)
class BaselineEvaluationRun:
    comparison: ModelComparison
    acceptance: AcceptanceAssessment
    report_path: Path | None


def run_baseline_evaluation(
    write_evaluation_report: bool = True,
) -> BaselineEvaluationRun:
    dataset = DatasetPreparationPipeline().prepare()
    labels = [category.value for category in ExpenseCategory]

    model_a, benchmark_a = train_model_a(
        dataset.X_train,
        dataset.y_train,
        test_row_count=len(dataset.X_test),
    )
    model_b, benchmark_b = train_model_b(
        dataset.X_train,
        dataset.y_train,
        test_row_count=len(dataset.X_test),
    )

    evaluator = ModelEvaluator()
    result_a = evaluator.evaluate(
        model_a,
        "Model A: TF-IDF",
        dataset.X_test,
        dataset.y_test,
        labels,
    )
    result_b = evaluator.evaluate(
        model_b,
        "Model B: TF-IDF + Amount",
        dataset.X_test,
        dataset.y_test,
        labels,
    )

    comparison = ModelComparison(
        model_a_metrics=result_a,
        model_b_metrics=result_b,
        model_a_experiment=benchmark_a["experiment"],
        model_b_experiment=benchmark_b["experiment"],
    )
    acceptance = assess_acceptance(
        result_a,
        AcceptanceCriteria(),
    )
    report_path = None
    if write_evaluation_report:
        report_path = write_report(
            comparison,
            acceptance,
            Path("artifacts/reports"),
        )

    return BaselineEvaluationRun(
        comparison=comparison,
        acceptance=acceptance,
        report_path=report_path,
    )


if __name__ == "__main__":
    evaluation_run = run_baseline_evaluation()
    print(evaluation_run.report_path)