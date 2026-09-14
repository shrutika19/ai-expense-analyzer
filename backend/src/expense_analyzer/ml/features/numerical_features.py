from decimal import Decimal

import numpy as np
import pandas as pd


class AmountFeatureTransformer:
    """Transforms expense amounts into a numeric ML feature."""

    FEATURE_NAME = "amount"

    def transform(
        self,
        amounts: pd.Series,
    ) -> np.ndarray:
        if amounts.isna().any():
            raise ValueError("Amount cannot contain missing values.")

        try:
            numeric_amounts = pd.to_numeric(
                amounts,
                errors="raise",
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Amount must contain valid numeric values."
            ) from exc

        if (numeric_amounts <= 0).any():
            raise ValueError(
                "Amount must contain only positive values."
            )

        return numeric_amounts.to_numpy(
            dtype=float,
        ).reshape(-1, 1)