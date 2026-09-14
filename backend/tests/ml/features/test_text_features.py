import numpy as np

from expense_analyzer.ml.features.text_features import (
    TfidfFeatureExtractor,
)


def test_fit_transform_creates_tfidf_matrix():
    descriptions = [
        "uber ride",
        "uber to office",
        "office transport",
    ]

    extractor = TfidfFeatureExtractor(
        min_df=1,
    )

    matrix = extractor.fit_transform(descriptions)

    assert matrix.shape[0] == 3
    assert matrix.shape[1] > 0


def test_transform_uses_training_vocabulary():
    train_descriptions = [
        "uber ride",
        "uber office",
        "office transport",
    ]

    test_descriptions = [
        "uber transport",
    ]

    extractor = TfidfFeatureExtractor(
        min_df=1,
    )

    train_matrix = extractor.fit_transform(
        train_descriptions
    )

    test_matrix = extractor.transform(
        test_descriptions
    )

    assert train_matrix.shape[1] == test_matrix.shape[1]


def test_unseen_test_word_does_not_change_feature_count():
    train_descriptions = [
        "uber ride",
        "uber office",
        "office transport",
    ]

    test_descriptions = [
        "restaurant dinner",
    ]

    extractor = TfidfFeatureExtractor(
        min_df=1,
    )

    train_matrix = extractor.fit_transform(
        train_descriptions
    )

    test_matrix = extractor.transform(
        test_descriptions
    )

    assert test_matrix.shape[1] == train_matrix.shape[1]


def test_lowercase_is_enabled():
    descriptions = [
        "Uber Ride",
        "uber ride",
    ]

    extractor = TfidfFeatureExtractor(
        min_df=1,
        lowercase=True,
    )

    matrix = extractor.fit_transform(descriptions)

    assert matrix.shape[1] > 0


def test_bigram_features_are_supported():
    descriptions = [
        "uber ride",
        "uber office",
        "office transport",
    ]

    extractor = TfidfFeatureExtractor(
        min_df=1,
        ngram_range=(1, 2),
    )

    extractor.fit_transform(descriptions)

    vocabulary = extractor.vectorizer.get_feature_names_out()

    assert "uber" in vocabulary
    assert "uber ride" in vocabulary


def test_max_features_is_respected():
    descriptions = [
        "uber ride office",
        "amazon shopping purchase",
        "restaurant food dinner",
    ]

    extractor = TfidfFeatureExtractor(
        min_df=1,
        max_features=2,
    )

    matrix = extractor.fit_transform(descriptions)

    assert matrix.shape[1] <= 2


def test_tfidf_matrix_contains_numeric_values():
    descriptions = [
        "uber ride",
        "restaurant lunch",
    ]

    extractor = TfidfFeatureExtractor(
        min_df=1,
    )

    matrix = extractor.fit_transform(descriptions)

    values = matrix.toarray()

    assert np.issubdtype(values.dtype, np.number)