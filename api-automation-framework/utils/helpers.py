"""Small framework helper functions."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parents[1]


def deep_get(payload: dict[str, Any], dotted_path: str, default: Any = None) -> Any:
    """Read a nested dictionary value using dot notation."""
    current: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current
