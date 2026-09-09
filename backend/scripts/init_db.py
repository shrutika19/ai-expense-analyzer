from expense_analyzer.infrastructure.database.init_db import (
    initialize_database,
)


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")