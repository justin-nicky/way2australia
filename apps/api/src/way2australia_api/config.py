from functools import lru_cache
from pathlib import Path
from typing import Literal, cast

from fastapi import Request
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnvironment = Literal["development", "staging", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    app_env: AppEnvironment = "development"
    app_debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)
    log_level: LogLevel = "INFO"
    # Serving (Spec 013 R16). `repo_root` is where config/, knowledge/ and the
    # lexical file live; `serving_config` is relative to it unless absolute.
    repo_root: Path = Field(default_factory=Path.cwd)
    serving_config: Path = Path("config/serving.yaml")
    # Fake embedder, reranker and generator (no model, no network, no key).
    api_fake: bool = Field(default=False, validation_alias="W2A_API_FAKE")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_request_settings(request: Request) -> Settings:
    settings = cast(Settings | None, getattr(request.app.state, "settings", None))
    if settings is not None:
        return settings
    return get_settings()
