from pathlib import Path

import pytest
from pydantic import ValidationError
from way2australia_api.config import Settings, get_settings
from way2australia_api.main import create_app


@pytest.fixture(autouse=True)
def isolate_settings_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    get_settings.cache_clear()
    monkeypatch.chdir(tmp_path)
    for name in ("APP_ENV", "APP_DEBUG", "API_HOST", "API_PORT", "LOG_LEVEL"):
        monkeypatch.delenv(name, raising=False)


def test_settings_defaults_without_env_file() -> None:
    settings = Settings()

    assert settings.app_env == "development"
    assert settings.app_debug is False
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000
    assert settings.log_level == "INFO"


def test_settings_load_from_env_file() -> None:
    Path(".env").write_text(
        "\n".join(
            [
                "APP_ENV=staging",
                "APP_DEBUG=true",
                "API_HOST=127.0.0.1",
                "API_PORT=9000",
                "LOG_LEVEL=DEBUG",
            ]
        ),
        encoding="utf-8",
    )

    settings = Settings()

    assert settings.app_env == "staging"
    assert settings.app_debug is True
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 9000
    assert settings.log_level == "DEBUG"


def test_settings_reject_invalid_port() -> None:
    with pytest.raises(ValidationError):
        Settings(api_port=70000)


def test_create_app_wires_settings() -> None:
    settings = Settings(app_debug=True)

    app = create_app(settings=settings)

    assert app.debug is True
    assert app.state.settings is settings
