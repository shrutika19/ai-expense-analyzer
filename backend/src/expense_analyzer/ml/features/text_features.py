from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass(frozen=True)
class TfidfFeatureMetadata:
    lowercase: bool
    ngram_range: tuple[int, int]
    min_df: int
    max_features: int
    vocabulary: tuple[str, ...]
    feature_names: tuple[str, ...]


class TfidfFeatureExtractor:
    """
    Extracts TF-IDF features from expense descriptions.

    The vectorizer must be fitted only on training data.
    """

    def __init__(
        self,
        max_features: int = 5000,
        min_df: int = 2,
        ngram_range: tuple[int, int] = (1, 2),
        lowercase: bool = True,
    ) -> None:
        self.max_features = max_features
        self.min_df = min_df
        self.ngram_range = ngram_range
        self.lowercase = lowercase

        self.vectorizer = TfidfVectorizer(
            lowercase=lowercase,
            ngram_range=ngram_range,
            min_df=min_df,
            max_features=max_features,
        )

    def fit_transform(self, descriptions: list[str]):
        return self.vectorizer.fit_transform(descriptions)

    def transform(self, descriptions: list[str]):
        return self.vectorizer.transform(descriptions)

    def get_metadata(self) -> TfidfFeatureMetadata:
        if not hasattr(self.vectorizer, "vocabulary_"):
            raise ValueError(
                "TF-IDF vectorizer has not been fitted."
            )

        vocabulary = tuple(
            sorted(self.vectorizer.vocabulary_.keys())
        )

        feature_names = tuple(
            self.vectorizer.get_feature_names_out()
        )

        return TfidfFeatureMetadata(
            lowercase=self.lowercase,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            max_features=self.max_features,
            vocabulary=vocabulary,
            feature_names=feature_names,
        )