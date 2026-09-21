from expense_analyzer.ml.evaluation.reporting import (
    format_comparison,
)
from expense_analyzer.ml.evaluation.run_baseline_evaluation import (
    run_baseline_evaluation,
)


def main() -> None:
    """Train and evaluate both baselines using one held-out test split."""

    evaluation_run = run_baseline_evaluation()
    print(format_comparison(evaluation_run.comparison))
    print(f"Acceptance: {evaluation_run.acceptance.decision}")
    print(f"Report: {evaluation_run.report_path}")


if __name__ == "__main__":
    main()
