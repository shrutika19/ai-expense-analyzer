from expense_analyzer.ml.evaluation.metrics import (
    calculate_accuracy,
    calculate_confusion_matrix,
    calculate_macro_f1,
    calculate_macro_precision,
    calculate_macro_recall,
    calculate_per_category_metrics,
    calculate_weighted_f1,
    calculate_weighted_precision,
    calculate_weighted_recall,
)
from expense_analyzer.ml.evaluation.result import (
    ModelEvaluationResult,
)
from expense_analyzer.ml.training.trainer import (
    TrainedModel,
)


class ModelEvaluator:
    """Evaluate already-trained classification models."""

    def evaluate(
        self,
        model: TrainedModel,
        model_name: str,
        X_test,
        y_test,
        labels: list[str],
    ) -> ModelEvaluationResult:
        """
        Evaluate a trained model using test data only.

        This method NEVER trains the model and NEVER fits
        the feature pipeline on test data.
        """

        # --------------------------------------------------
        # Step 5: Transform X_test using the already-fitted
        # feature pipeline.
        # --------------------------------------------------

        X_test_features = (
            model.feature_pipeline.transform(X_test)
        )

        # --------------------------------------------------
        # Step 5: Generate predictions.
        # --------------------------------------------------

        y_pred = model.classifier.predict(
            X_test_features
        )

        # --------------------------------------------------
        # Step 6 / Step 7: Overall metrics.
        # --------------------------------------------------

        accuracy = calculate_accuracy(
            y_test,
            y_pred,
        )

        macro_precision = calculate_macro_precision(
            y_test,
            y_pred,
        )

        macro_recall = calculate_macro_recall(
            y_test,
            y_pred,
        )

        macro_f1 = calculate_macro_f1(
            y_test,
            y_pred,
        )

        weighted_precision = calculate_weighted_precision(
            y_test,
            y_pred,
        )

        weighted_recall = calculate_weighted_recall(
            y_test,
            y_pred,
        )

        weighted_f1 = calculate_weighted_f1(
            y_test,
            y_pred,
        )

        # --------------------------------------------------
        # Step 6 / Step 7: Per-category metrics.
        # --------------------------------------------------

        per_category_metrics = (
            calculate_per_category_metrics(
                y_true=y_test,
                y_pred=y_pred,
                labels=labels,
            )
        )

        # --------------------------------------------------
        # Step 6 / Step 7: Confusion matrix.
        # --------------------------------------------------

        matrix = calculate_confusion_matrix(
            y_true=y_test,
            y_pred=y_pred,
            labels=labels,
        )

        # --------------------------------------------------
        # Step 8: Return structured evaluation result.
        # --------------------------------------------------

        return ModelEvaluationResult(
            model_name=model_name,
            accuracy=accuracy,
            macro_precision=macro_precision,
            macro_recall=macro_recall,
            macro_f1=macro_f1,
            weighted_precision=weighted_precision,
            weighted_recall=weighted_recall,
            weighted_f1=weighted_f1,
            per_category_metrics=per_category_metrics,
            confusion_matrix=matrix,
            labels=tuple(labels),
        )