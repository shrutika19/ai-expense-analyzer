from functools import lru_cache
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Expense Analyzer"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    cors_allowed_origins: list[str] = [
        "http://localhost:5173",
    ]

    # Database configuration
    database_host: str
    database_port: int = 5432
    database_name: str
    database_user: str
    database_password: str

    # JWT configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_issuer: str = "ai-expense-analyzer"
    jwt_audience: str = "ai-expense-analyzer-api"

    # ML model configuration
    # The server decides which model version is active.
    # Clients cannot select the model version.
    model_version: str = "v1.0.0"
    model_artifacts_directory: str = "artifacts/models"
    ml_confidence_threshold: float = 0.70

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()