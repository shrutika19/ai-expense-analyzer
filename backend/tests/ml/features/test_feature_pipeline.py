from decimal import Decimal

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from scipy.sparse import csr_matrix

from expense_analyzer.ml.features.feature_pipeline import (
    FeaturePipeline,
)


def create_train_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "description": [
                "uber ride",
                "uber office",
                "restaurant lunch",
                "grocery shopping",
                "uber transport",
                "restaurant dinner",
            ],
            "amount": [
                Decimal("350.00"),
                Decimal("500.00"),
                Decimal("250.00"),
                Decimal("1200.00"),
                Decimal("400.00"),
                Decimal("600.00"),
            ],
            "category": [
                "TRANSPORT",
                "TRANSPORT",
                "FOOD",
                "SHOPPING",
                "TRANSPORT",
                "FOOD",
            ],
        }
    )


def create_test_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "description": [
                "uber ride",
                "restaurant dinner",
            ],
            "amount": [
                Decimal("400.00"),
                Decimal("600.00"),
            ],
            "category": [
                "TRANSPORT",
                "FOOD",
            ],
        }
    )


def test_training_data_produces_expected_matrix_shape():
    train_data = create_train_data()

    pipeline = FeaturePipeline(
        include_amount=True,
    )

    matrix = pipeline.fit_transform(train_data)

    assert isinstance(matrix, csr_matrix)
    assert matrix.shape[0] == len(train_data)
    assert matrix.shape[1] > 1


def test_test_data_has_identical_feature_dimensions():
    train_data = create_train_data()
    test_data = create_test_data()

    pipeline = FeaturePipeline(
        include_amount=True,
    )

    pipeline.fit_transform(train_data)
    test_matrix = pipeline.transform(test_data)

    assert test_matrix.shape[0] == len(test_data)
    assert test_matrix.shape[1] == pipeline.fit_transform(
        train_data
    ).shape[1]


def test_description_and_amount_remain_aligned():
    train_data = create_train_data()

    pipeline = FeaturePipeline(
        include_amount=True,
    )

    matrix = pipeline.fit_transform(train_data)

    assert matrix.shape[0] == len(train_data)

    amount_feature = matrix[:, -1].toarray().flatten()

    expected_amounts = [
        350.0,
        500.0,
        250.0,
        1200.0,
        400.0,
        600.0,
    ]

    assert amount_feature.tolist() == expected_amounts


def test_category_does_not_enter_feature_matrix():
    train_data = create_train_data()

    pipeline = FeaturePipeline(
        include_amount=True,
    )

    matrix_with_category = pipeline.fit_transform(
        train_data
    )

    train_without_category = train_data.drop(
        columns=["category"]
    )

    pipeline_without_category = FeaturePipeline(
        include_amount=True,
    )

    matrix_without_category = (
        pipeline_without_category.fit_transform(
            train_without_category
        )
    )

    assert matrix_with_category.shape == (
        matrix_without_category.shape
    )

    assert (
        matrix_with_category != matrix_without_category
    ).nnz == 0


def test_vectorizer_is_fitted_only_on_training_data():
    train_data = create_train_data()
    test_data = create_test_data()

    pipeline = FeaturePipeline(
        include_amount=False,
    )

    pipeline.fit_transform(train_data)

    metadata_before = pipeline.get_metadata()

    pipeline.transform(test_data)

    metadata_after = pipeline.get_metadata()

    assert metadata_before == metadata_after


def test_test_data_does_not_modify_vocabulary():
    train_data = create_train_data()

    test_data = pd.DataFrame(
        {
            "description": [
                "completely unseen vocabulary",
            ],
            "amount": [
                Decimal("900.00"),
            ],
        }
    )

    pipeline = FeaturePipeline(
        include_amount=False,
    )

    pipeline.fit_transform(train_data)

    vocabulary_before = pipeline.get_metadata().tfidf.vocabulary

    pipeline.transform(test_data)

    vocabulary_after = pipeline.get_metadata().tfidf.vocabulary

    assert vocabulary_before == vocabulary_after


def test_empty_training_dataset_is_handled():
    train_data = pd.DataFrame(
        {
            "description": pd.Series(dtype="object"),
            "amount": pd.Series(dtype="float64"),
        }
    )

    pipeline = FeaturePipeline(
        include_amount=True,
    )

    with pytest.raises(ValueError):
        pipeline.fit_transform(train_data)


def test_empty_test_dataset_is_handled():
    train_data = create_train_data()

    test_data = pd.DataFrame(
        {
            "description": pd.Series(dtype="object"),
            "amount": pd.Series(dtype="float64"),
        }
    )

    pipeline = FeaturePipeline(
        include_amount=True,
    )

    pipeline.fit_transform(train_data)

    with pytest.raises(ValueError):
        pipeline.transform(test_data)


def test_feature_transformation_is_deterministic():
    train_data = create_train_data()

    pipeline_1 = FeaturePipeline(
        include_amount=True,
    )

    pipeline_2 = FeaturePipeline(
        include_amount=True,
    )

    matrix_1 = pipeline_1.fit_transform(train_data)
    matrix_2 = pipeline_2.fit_transform(train_data)

    assert (matrix_1 != matrix_2).nnz == 0


def test_feature_metadata_contains_tfidf_configuration():
    train_data = create_train_data()

    pipeline = FeaturePipeline(
        include_amount=True,
    )

    pipeline.fit_transform(train_data)

    metadata = pipeline.get_metadata()

    assert metadata.tfidf.lowercase is True
    assert metadata.tfidf.ngram_range == (1, 2)
    assert metadata.tfidf.min_df == 2
    assert metadata.tfidf.max_features == 5000


def test_feature_metadata_contains_vocabulary_and_feature_names():
    train_data = create_train_data()

    pipeline = FeaturePipeline(
        include_amount=True,
    )

    pipeline.fit_transform(train_data)

    metadata = pipeline.get_metadata()

    assert len(metadata.tfidf.vocabulary) > 0
    assert len(metadata.tfidf.feature_names) > 0

    assert set(metadata.tfidf.vocabulary) == set(
        metadata.tfidf.feature_names
    )


def test_feature_metadata_contains_numerical_configuration():
    train_data = create_train_data()

    pipeline = FeaturePipeline(
        include_amount=True,
    )

    pipeline.fit_transform(train_data)

    metadata = pipeline.get_metadata()

    assert metadata.include_amount is True
    assert metadata.numerical_features == ("amount",)


def test_feature_metadata_excludes_amount_when_disabled():
    train_data = create_train_data()

    pipeline = FeaturePipeline(
        include_amount=False,
    )

    pipeline.fit_transform(train_data)

    metadata = pipeline.get_metadata()

    assert metadata.include_amount is False
    assert metadata.numerical_features == ()