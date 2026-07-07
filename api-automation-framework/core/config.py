"""Environment-aware configuration loading for test execution."""

from __future__ import annotations

import configparser
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

from core.exceptions import ConfigurationError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


@dataclass(frozen=True, slots=True)
class FrameworkConfig:
    """Immutable runtime settings for API tests."""

    environment: str
    base_url: str
    timeout_seconds: float
    verify_ssl: bool
    retry_total: int
    retry_backoff_factor: float
    api_key: str | None = None
    bearer_token: str | None = None
    username: str | None = None
    password: str | None = None
    oauth_token_url: str | None = None
    client_id: str | None = None
    client_secret: str | None = None

    @classmethod
    def load(cls, environment: str) -> "FrameworkConfig":
        """Load configuration from config.ini, environment files, and process env."""
        env_name = environment.lower().strip()
        if env_name not in {"qa", "uat", "prod"}:
            raise ConfigurationError("Environment must be one of: qa, uat, prod.")

        ini_path = CONFIG_DIR / "config.ini"
        env_path = CONFIG_DIR / f"{env_name}.env"
        if not ini_path.exists():
            raise ConfigurationError(f"Missing configuration file: {ini_path}")
        if not env_path.exists():
            raise ConfigurationError(f"Missing environment file: {env_path}")

        parser = configparser.ConfigParser()
        parser.read(ini_path)
        defaults = parser["framework"] if parser.has_section("framework") else {}
        env_file_values = dotenv_values(env_path)
        merged = {**dict(defaults), **env_file_values, **os.environ}

        base_url = _required(merged, "BASE_URL").rstrip("/")
        return cls(
            environment=env_name,
            base_url=base_url,
            timeout_seconds=_float_value(merged, "TIMEOUT_SECONDS", 30.0),
            verify_ssl=_bool_value(merged, "VERIFY_SSL", True),
            retry_total=_int_value(merged, "RETRY_TOTAL", 3),
            retry_backoff_factor=_float_value(merged, "RETRY_BACKOFF_FACTOR", 0.5),
            api_key=_optional(merged, "API_KEY"),
            bearer_token=_optional(merged, "BEARER_TOKEN"),
            username=_optional(merged, "USERNAME"),
            password=_optional(merged, "PASSWORD"),
            oauth_token_url=_optional(merged, "OAUTH_TOKEN_URL"),
            client_id=_optional(merged, "CLIENT_ID"),
            client_secret=_optional(merged, "CLIENT_SECRET"),
        )


def _required(values: dict[str, Any], key: str) -> str:
    """Return a required configuration value or raise a clear error."""
    value = values.get(key)
    if value is None or str(value).strip() == "":
        raise ConfigurationError(f"Missing required configuration value: {key}")
    return str(value)


def _optional(values: dict[str, Any], key: str) -> str | None:
    """Return an optional configuration value."""
    value = values.get(key)
    if value is None or str(value).strip() == "":
        return None
    return str(value)


def _bool_value(values: dict[str, Any], key: str, default: bool) -> bool:
    """Parse a boolean configuration value."""
    value = values.get(key, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _int_value(values: dict[str, Any], key: str, default: int) -> int:
    """Parse an integer configuration value."""
    value = values.get(key, default)
    try:
        return int(str(value))
    except ValueError as exc:
        raise ConfigurationError(f"{key} must be an integer.") from exc


def _float_value(values: dict[str, Any], key: str, default: float) -> float:
    """Parse a float configuration value."""
    value = values.get(key, default)
    try:
        return float(str(value))
    except ValueError as exc:
        raise ConfigurationError(f"{key} must be a number.") from exc
