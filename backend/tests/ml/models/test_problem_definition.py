from expense_analyzer.ml.models.problem_definition import (
    CategoryPredictionProblem,
)


def test_category_prediction_problem_definition():
    problem = CategoryPredictionProblem()

    assert problem.name == "expense_category_prediction"
    assert problem.task_type == "multiclass_classification"
    assert problem.input_features == (
        "description",
        "amount",
    )
    assert problem.target == "category"