import json

from expense_analyzer.ml.evaluation.acceptance import (
    AcceptanceCriteria,
    assess_acceptance,
)
from expense_analyzer.ml.evaluation.comparison import ModelComparison
from expense_analyzer.ml.evaluation.reporting import (
    format_comparison,
    write_report,
)
from tests.ml.evaluation.test_acceptance import create_result


def test_comparison_format_and_report_serialization(tmp_path):
    comparison = ModelComparison(
        model_a_metrics=create_result(0.8),
        model_b_metrics=create_result(0.7),
    )
    acceptance = assess_acceptance(
        comparison.model_a_metrics,
        AcceptanceCriteria(),
    )

    report_path = write_report(comparison, acceptance, tmp_path)

    assert "Macro F1" in format_comparison(comparison)
    assert "Model A" in format_comparison(comparison)
    assert report_path.exists()
    assert json.loads(report_path.read_text(encoding="utf-8"))["acceptance"]["decision"] == "not_configured"