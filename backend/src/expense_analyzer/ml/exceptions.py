class MLInferenceError(Exception):
    """Base exception for ML inference errors."""


class ModelUnavailableError(MLInferenceError):
    """Raised when the requested model cannot be loaded or used."""


class ModelArtifactNotFoundError(ModelUnavailableError):
    """Raised when the model artifact does not exist."""


class ModelLoadError(ModelUnavailableError):
    """Raised when a model artifact cannot be loaded."""


class ModelCompatibilityError(ModelUnavailableError):
    """Raised when a model artifact is incompatible with the application."""


class PredictorUnavailableError(MLInferenceError):
    """Raised when the predictor cannot perform inference."""