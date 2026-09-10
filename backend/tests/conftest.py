import os

import pytest

os.environ["ENV_FILE"] = ".env.test"


@pytest.fixture(scope="session", autouse=True)
def initialize_test_database() -> None:
	from expense_analyzer.infrastructure.database.init_db import (
		initialize_database,
	)

	initialize_database()