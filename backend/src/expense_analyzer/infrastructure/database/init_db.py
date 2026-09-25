from expense_analyzer.infrastructure.database.connection import (
    get_connection,
)


CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


CREATE_EXPENSES_TABLE = """
CREATE TABLE IF NOT EXISTS expenses (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    description VARCHAR(500) NOT NULL,
    category VARCHAR(50) NOT NULL,
    expense_date DATE NOT NULL,
    category_source VARCHAR(20) NOT NULL DEFAULT 'manual',
    predicted_category VARCHAR(50),
    category_confidence DOUBLE PRECISION,
    model_version VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_expenses_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
"""

# Kept separate from CREATE so deployments with an existing table retain the
# original model output needed to compare it with a later user correction.
ADD_PREDICTED_CATEGORY_COLUMN = """
ALTER TABLE expenses
ADD COLUMN IF NOT EXISTS predicted_category VARCHAR(50);
"""


def initialize_database() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_USERS_TABLE)
            cursor.execute(CREATE_EXPENSES_TABLE)
            cursor.execute(ADD_PREDICTED_CATEGORY_COLUMN)

        connection.commit()
