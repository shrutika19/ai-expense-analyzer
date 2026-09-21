import uuid
from datetime import date

from expense_analyzer.infrastructure.database.connection import get_connection


USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


EXPENSES = [
    # Food
    ("Restaurant dinner", 850.00, "Food"),
    ("Pizza delivery", 450.00, "Food"),
    ("Lunch at restaurant", 600.00, "Food"),
    ("Grocery food purchase", 1200.00, "Food"),

    # Transport
    ("Uber ride to office", 250.00, "Transport"),
    ("Taxi to airport", 900.00, "Transport"),
    ("Metro travel", 100.00, "Transport"),
    ("Bus ticket", 50.00, "Transport"),

    # Travel
    ("Flight ticket", 6500.00, "Travel"),
    ("Hotel booking", 4500.00, "Travel"),
    ("Train ticket", 1800.00, "Travel"),
    ("Vacation booking", 10000.00, "Travel"),

    # Shopping
    ("Amazon household purchase", 1500.00, "Shopping"),
    ("Clothes purchase", 2200.00, "Shopping"),
    ("Online shopping", 1800.00, "Shopping"),
    ("New shoes", 3000.00, "Shopping"),

    # Entertainment
    ("Netflix subscription", 649.00, "Entertainment"),
    ("Movie tickets", 800.00, "Entertainment"),
    ("Concert tickets", 2500.00, "Entertainment"),
    ("Music subscription", 199.00, "Entertainment"),

    # Utilities
    ("Electricity bill", 1800.00, "Utilities"),
    ("Gas bill", 900.00, "Utilities"),
    ("Water utility payment", 500.00, "Utilities"),
    ("Internet bill", 999.00, "Utilities"),

    # Healthcare
    ("Doctor consultation", 1000.00, "Healthcare"),
    ("Pharmacy medicine", 750.00, "Healthcare"),
    ("Dental treatment", 2500.00, "Healthcare"),
    ("Medical checkup", 1500.00, "Healthcare"),

    # Education
    ("Online course", 2000.00, "Education"),
    ("Books for course", 1200.00, "Education"),
    ("Training subscription", 3000.00, "Education"),
    ("Programming course", 2500.00, "Education"),

    # Rent
    ("Monthly house rent", 25000.00, "Rent"),
    ("Apartment rent", 22000.00, "Rent"),
    ("Monthly rental payment", 28000.00, "Rent"),
    ("House rent payment", 24000.00, "Rent"),

    # Other
    ("Miscellaneous expense", 500.00, "Other"),
    ("General expense", 700.00, "Other"),
    ("Personal expense", 900.00, "Other"),
    ("Other payment", 400.00, "Other"),
]


def seed_ml_dataset() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:

            # Create a deterministic CI test user.
            cursor.execute(
                """
                INSERT INTO users (
                    id,
                    email,
                    password_hash,
                    is_active
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    TRUE
                )
                ON CONFLICT (id) DO NOTHING;
                """,
                (
                    USER_ID,
                    "ml-ci-test@example.com",
                    "ci-test-password-hash",
                ),
            )

            # Insert deterministic ML training records.
            for description, amount, category in EXPENSES:
                cursor.execute(
                    """
                    INSERT INTO expenses (
                        id,
                        user_id,
                        amount,
                        description,
                        category,
                        expense_date
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    );
                    """,
                    (
                        uuid.uuid4(),
                        USER_ID,
                        amount,
                        description,
                        category,
                        date.today(),
                    ),
                )

        connection.commit()


if __name__ == "__main__":
    seed_ml_dataset()
    print(
        f"ML dataset seeded successfully: "
        f"{len(EXPENSES)} expense records."
    )