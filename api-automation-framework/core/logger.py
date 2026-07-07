"""Centralized logging utilities for framework execution."""

from __future__ import annotations

import json
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

DEFAULT_LOG_DIR = Path(__file__).resolve().parents[1] / "logs"


def get_logger(name: str = "api_automation") -> logging.Logger:
    """Return a configured logger with console and rotating file handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        DEFAULT_LOG_DIR / "framework.log",
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def sanitize_mapping(data: dict[str, Any] | None) -> dict[str, Any]:
    """Mask sensitive values in a mapping before logging."""
    if not data:
        return {}

    sensitive_keys = {"authorization", "token", "api-key", "apikey", "password", "secret"}
    sanitized: dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys or any(part in key.lower() for part in sensitive_keys):
            sanitized[key] = "***MASKED***"
        else:
            sanitized[key] = value
    return sanitized


def to_pretty_json(data: Any) -> str:
    """Return a compact JSON representation suitable for log messages."""
    try:
        return json.dumps(data, indent=2, sort_keys=True, default=str)
    except TypeError:
        return str(data)
