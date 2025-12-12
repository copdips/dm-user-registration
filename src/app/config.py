"""Application settings"""

from functools import cached_property

from pydantic import Field
from pydantic.fields import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

import app

DEFAULT_APP_ENV = "dev"


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
    app_env: str = Field(default=DEFAULT_APP_ENV)

    @computed_field
    @cached_property
    def app_title(self) -> str:
        return f"[{self.app_env}] {self.app_name} ({self.app_version})"

    @computed_field
    @cached_property
    def app_description(self) -> str:
        return self.app_title

    @computed_field
    @cached_property
    def debug(self) -> bool:
        return self.app_env == DEFAULT_APP_ENV

    # Database
    database_url: str = Field(default=...)

    # Redis
    redis_url: str = Field(default=...)

    # Verification code
    verification_code_ttl_seconds: int = 60


settings = Settings()
