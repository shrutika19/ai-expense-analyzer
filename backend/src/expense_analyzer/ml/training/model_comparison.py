from dataclasses import dataclass


@dataclass(frozen=True)
class ModelComparison:
    """
    Describes the baseline models being compared.

    Evaluation metrics are intentionally not included yet.
    They will be added during Phase 6.
    """

    model_a_name: str = "baseline_tfidf_logistic_model_a"
    model_b_name: str = "baseline_tfidf_logistic_model_b"

    model_a_features: str = "TF-IDF(description)"
    model_b_features: str = "TF-IDF(description) + amount"

    model_a_amount_included: bool = False
    model_b_amount_included: bool = True