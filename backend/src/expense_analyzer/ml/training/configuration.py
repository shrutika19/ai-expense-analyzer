from dataclasses import dataclass, field


@dataclass(frozen=True)
class TfidfConfiguration:
    lowercase: bool = True
    ngram_range: tuple[int, int] = (1, 2)
    min_df: int = 2
    max_features: int = 5000


@dataclass(frozen=True)
class LogisticRegressionConfiguration:
    max_iterations: int = 3000
    random_state: int = 42


@dataclass(frozen=True)
class TrainingConfiguration:
    model: LogisticRegressionConfiguration = field(
        default_factory=LogisticRegressionConfiguration
    )

    tfidf: TfidfConfiguration = field(
        default_factory=TfidfConfiguration
    )

    include_amount: bool = True