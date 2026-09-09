from contextlib import contextmanager
from typing import Generator

import psycopg

from expense_analyzer.core.config import get_settings


@contextmanager
def get_connection() -> Generator[psycopg.Connection, None, None]:
    settings = get_settings()

    connection = psycopg.connect(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
    )

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()