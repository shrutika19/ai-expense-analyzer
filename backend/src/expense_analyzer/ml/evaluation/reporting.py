import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from expense_analyzer.ml.evaluation.acceptance import (
    AcceptanceAssessment,
)
from expense_analyzer.ml.evaluation.comparison import (
    ModelComparison,
    get_macro_f1_winner,
)


def format_comparison(
    comparison: ModelComparison,
) -> str:
    model_a = comparison.model_a_metrics
    model_b = comparison.model_b_metrics

    if model_a is None or model_b is None:
        return "Evaluation metrics are not available."

    rows = [
        ("Accuracy", model_a.accuracy, model_b.accuracy),
        ("Macro Precision", model_a.macro_precision, model_b.macro_precision),
        ("Macro Recall", model_a.macro_recall, model_b.macro_recall),
        ("Macro F1", model_a.macro_f1, model_b.macro_f1),
        ("Weighted Precision", model_a.weighted_precision, model_b.weighted_precision),
        ("Weighted Recall", model_a.weighted_recall, model_b.weighted_recall),
        ("Weighted F1", model_a.weighted_f1, model_b.weighted_f1),
    ]
    lines = [
        f"{'Metric':<20}{'Model A: TF-IDF':>18}{'Model B: TF-IDF + Amount':>27}",
    ]
    lines.extend(
        f"{name:<20}{model_a_value:>18.4f}{model_b_value:>27.4f}"
        for name, model_a_value, model_b_value in rows
    )
    lines.append(f"Macro F1 winner: {get_macro_f1_winner(comparison)}")
    return "\n".join(lines)


def write_report(
    comparison: ModelComparison,
    acceptance: AcceptanceAssessment,
    output_directory: Path,
) -> Path:
    output_directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_directory / f"baseline_evaluation_{timestamp}.json"

    payload = {
        "comparison": asdict(comparison),
        "macro_f1_winner": get_macro_f1_winner(comparison),
        "comparison_table": format_comparison(comparison),
        "acceptance": asdict(acceptance),
    }
    report_path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    return report_path