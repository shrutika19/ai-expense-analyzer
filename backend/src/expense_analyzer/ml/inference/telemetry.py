from dataclasses import dataclass
from threading import Lock


@dataclass
class InferenceTelemetry:
    prediction_count: int = 0
    failure_count: int = 0
    low_confidence_count: int = 0
    fallback_count: int = 0
    total_latency_ms: float = 0.0

    def __post_init__(self) -> None:
        self._lock = Lock()

    def record_prediction(self, latency_ms: float, low_confidence: bool) -> None:
        with self._lock:
            self.prediction_count += 1
            self.total_latency_ms += latency_ms
            self.low_confidence_count += int(low_confidence)

    def record_failure(self) -> None:
        with self._lock:
            self.failure_count += 1

    def record_fallback(self) -> None:
        with self._lock:
            self.fallback_count += 1

    def snapshot(self, model_version: str) -> dict:
        with self._lock:
            return {"prediction_count": self.prediction_count, "inference_failure_count": self.failure_count,
                    "low_confidence_count": self.low_confidence_count, "fallback_count": self.fallback_count,
                    "average_inference_latency_ms": (self.total_latency_ms / self.prediction_count if self.prediction_count else None),
                    "predictions_by_model_version": {model_version: self.prediction_count}}
