from pathlib import Path

import pandas as pd

from expense_analyzer.ml.training.trainer import CategoryModelTrainer


TRAINING_DATA = [
    # Food
    ("Restaurant dinner", 850.0, "Food"),
    ("Pizza delivery", 450.0, "Food"),
    ("Lunch at restaurant", 600.0, "Food"),
    ("Grocery food purchase", 1200.0, "Food"),
    ("Coffee and breakfast", 300.0, "Food"),

    # Transport
    ("Uber ride to office", 250.0, "Transport"),
    ("Taxi to airport", 900.0, "Transport"),
    ("Metro travel", 100.0, "Transport"),
    ("Bus ticket", 50.0, "Transport"),
    ("Cab ride home", 300.0, "Transport"),

    # Travel
    ("Flight ticket", 6500.0, "Travel"),
    ("Hotel booking", 4500.0, "Travel"),
    ("Train ticket", 1800.0, "Travel"),
    ("Vacation booking", 10000.0, "Travel"),
    ("Travel insurance", 2000.0, "Travel"),

    # Shopping
    ("Amazon household purchase", 1500.0, "Shopping"),
    ("Clothes purchase", 2200.0, "Shopping"),
    ("Online shopping", 1800.0, "Shopping"),
    ("New shoes", 3000.0, "Shopping"),
    ("Grocery shopping", 2000.0, "Shopping"),

    # Entertainment
    ("Netflix subscription", 649.0, "Entertainment"),
    ("Movie tickets", 800.0, "Entertainment"),
    ("Concert tickets", 2500.0, "Entertainment"),
    ("Music subscription", 199.0, "Entertainment"),
    ("Gaming subscription", 499.0, "Entertainment"),

    # Utilities
    ("Electricity bill", 1800.0, "Utilities"),
    ("Gas bill", 900.0, "Utilities"),
    ("Water utility payment", 500.0, "Utilities"),
    ("Internet bill", 999.0, "Utilities"),
    ("Mobile utility payment", 699.0, "Utilities"),

    # Healthcare
    ("Doctor consultation", 1000.0, "Healthcare"),
    ("Pharmacy medicine", 750.0, "Healthcare"),
    ("Dental treatment", 2500.0, "Healthcare"),
    ("Medical checkup", 1500.0, "Healthcare"),
    ("Health consultation", 800.0, "Healthcare"),

    # Education
    ("Online course", 2000.0, "Education"),
    ("Books for course", 1200.0, "Education"),
    ("Training subscription", 3000.0, "Education"),
    ("Programming course", 2500.0, "Education"),
    ("Study materials", 900.0, "Education"),

    # Rent
    ("Monthly house rent", 25000.0, "Rent"),
    ("Apartment rent", 22000.0, "Rent"),
    ("Monthly rental payment", 28000.0, "Rent"),
    ("House rent payment", 24000.0, "Rent"),
    ("Room rent", 18000.0, "Rent"),

    # Other
    ("Miscellaneous expense", 500.0, "Other"),
    ("General expense", 700.0, "Other"),
    ("Personal expense", 900.0, "Other"),
    ("Other payment", 400.0, "Other"),
    ("Miscellaneous payment", 600.0, "Other"),
]


def main() -> None:
    dataframe = pd.DataFrame(
        TRAINING_DATA,
        columns=[
            "description",
            "amount",
            "category",
        ],
    )

    X = dataframe[
        [
            "description",
            "amount",
        ]
    ]

    y = dataframe["category"]

    trainer = CategoryModelTrainer()

    trained_model = trainer.train(
        X_train=X,
        y_train=y,
    )

    output_directory = (
        Path(__file__).resolve().parents[1]
        / "tests"
        / "fixtures"
        / "models"
        / "expense_category"
        / "v1.0.0"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    import joblib

    model_path = output_directory / "model.joblib"

    joblib.dump(
        trained_model,
        model_path,
    )

    print(
        f"Test model created successfully: {model_path}"
    )


if __name__ == "__main__":
    main()