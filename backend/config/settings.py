"""
Centralized Configuration Management using Pydantic Settings.
"""

from typing import Optional, List
from enum import Enum
from pathlib import Path
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """
    Application settings derived from environment variables.
    """

    # Application Configuration
    PROJECT_NAME: str = Field(default="FinSight AI", description="Name of the project")
    API_V1_STR: str = Field(default="/api/v1", description="API Version 1 Prefix")
    APP_ENV: AppEnvironment = Field(
        default=AppEnvironment.DEVELOPMENT, description="Application Environment"
    )

    # Security & CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["*"], description="List of origins allowed for CORS requests."
    )

    # Database Configuration
    POSTGRES_SERVER: str = Field(
        default="localhost", description="PostgreSQL server hostname"
    )
    POSTGRES_USER: str = Field(default="postgres", description="PostgreSQL user")
    POSTGRES_PASSWORD: SecretStr = Field(
        default=SecretStr("password"), description="PostgreSQL password"
    )
    POSTGRES_DB: str = Field(
        default="finsight_db", description="PostgreSQL database name"
    )
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")

    # LLM Settings

    MISTRAL_API_KEY: Optional[SecretStr] = Field(
        default=None, description="Mistral API Key"
    )
    LLM_PROVIDER: str = Field(default="mistral", description="The LLM Provider to use")

    # Workflow Settings
    EXPORTS_DIR: str = Field(
        default="backend/exports", description="Root directory for generated exports"
    )

    @property
    def uploads_dir(self) -> Path:
        return Path(self.EXPORTS_DIR) / "uploads"

    @property
    def workflows_dir(self) -> Path:
        return Path(self.EXPORTS_DIR) / "workflows"

    @property
    def sqlalchemy_database_uri(self) -> str:
        """
        Construct the database URI from components.
        """
        import urllib.parse

        encoded_password = urllib.parse.quote_plus(
            self.POSTGRES_PASSWORD.get_secret_value()
        )
        return f"postgresql://{self.POSTGRES_USER}:{encoded_password}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


# Dependency injection instance for configuration
settings = Settings()
