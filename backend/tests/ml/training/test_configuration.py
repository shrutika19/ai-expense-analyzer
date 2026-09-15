from expense_analyzer.ml.training.configuration import (
    LogisticRegressionConfiguration,
    TfidfConfiguration,
    TrainingConfiguration,
)


def test_default_training_configuration():
    config = TrainingConfiguration()

    assert config.include_amount is True


def test_default_logistic_regression_configuration():
    config = TrainingConfiguration()

    assert config.model.max_iterations == 1000
    assert config.model.random_state == 42


def test_default_tfidf_configuration():
    config = TrainingConfiguration()

    assert config.tfidf.lowercase is True
    assert config.tfidf.ngram_range == (1, 2)
    assert config.tfidf.min_df == 2
    assert config.tfidf.max_features == 5000


def test_amount_feature_can_be_disabled():
    config = TrainingConfiguration(
        include_amount=False
    )

    assert config.include_amount is False


def test_tfidf_configuration_can_be_customized():
    config = TrainingConfiguration(
        tfidf=TfidfConfiguration(
            lowercase=False,
            ngram_range=(1, 3),
            min_df=3,
            max_features=10000,
        )
    )

    assert config.tfidf.lowercase is False
    assert config.tfidf.ngram_range == (1, 3)
    assert config.tfidf.min_df == 3
    assert config.tfidf.max_features == 10000


def test_logistic_regression_configuration_can_be_customized():
    config = TrainingConfiguration(
        model=LogisticRegressionConfiguration(
            max_iterations=2000,
            random_state=123,
        )
    )

    assert config.model.max_iterations == 2000
    assert config.model.random_state == 123


def test_training_configuration_is_immutable():
    config = TrainingConfiguration()

    try:
        config.include_amount = False
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "TrainingConfiguration should be immutable."
        )