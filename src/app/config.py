"""Application settings"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

import app


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "User Registration API"
    app_version: str = getattr(app, "__version__", "0.0.0")
    app_title: str = f"{app_name} - ({app_version})"
    app_description: str = app_title
    debug: bool = False

    # Database
    database_url: str = Field(default=...)

    # Redis
    redis_url: str = Field(default=...)

    # Verification code
    verification_code_ttl_seconds: int = 60


settings = Settings()
