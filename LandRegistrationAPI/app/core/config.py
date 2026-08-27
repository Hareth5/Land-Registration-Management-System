from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "Land Registration Management System"
    MONGO_DB_NAME: str = Field(
        default="land_registration",
        validation_alias=AliasChoices("MONGO_DB_NAME", "DATABASE_NAME"),
    )
    MONGO_URI: str = Field(
        default="mongodb://127.0.0.1:27017",
        validation_alias=AliasChoices("MONGO_URI", "MONGODB_URL"),
    )
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = 5000

    SECRET_KEY: SecretStr | None = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    CORS_ORIGINS: str = (
        "http://127.0.0.1:5173,http://localhost:5173,"
        "http://127.0.0.1:5500,http://localhost:5500"
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def DATABASE_NAME(self) -> str:
        """Backward-compatible alias for older project configuration."""
        return self.MONGO_DB_NAME

    @property
    def MONGODB_URL(self) -> str:
        """Backward-compatible alias for older project configuration."""
        return self.MONGO_URI


settings = Settings()
