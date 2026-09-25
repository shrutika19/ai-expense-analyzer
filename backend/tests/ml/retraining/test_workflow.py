from expense_analyzer.ml.retraining.workflow import ControlledRetrainingWorkflow, RetrainingRules


def test_retraining_requires_a_measurable_trigger_and_never_auto_deploys():
    workflow = ControlledRetrainingWorkflow(RetrainingRules(minimum_new_labels=10))

    not_ready = workflow.assess_eligibility(
        new_labeled_count=2, correction_rate=0.01, distribution_change=0.01,
        new_category=False, scheduled_review_due=False,
    )
    ready = workflow.assess_eligibility(
        new_labeled_count=10, correction_rate=0.01, distribution_change=0.01,
        new_category=False, scheduled_review_due=False,
    )

    assert not_ready["retraining_allowed"] is False
    assert ready["retraining_allowed"] is True
    assert ready["automatic_deployment"] is False
