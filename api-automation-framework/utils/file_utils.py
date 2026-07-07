"""General file helpers for test data."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml


def read_text(path: str | Path) -> str:
    """Read a UTF-8 text file."""
    return Path(path).read_text(encoding="utf-8")


def read_csv(path: str | Path) -> list[dict[str, str]]:
    """Read CSV rows as dictionaries."""
    with Path(path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def read_yaml(path: str | Path) -> Any:
    """Read YAML content from disk."""
    with Path(path).open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def ensure_directory(path: str | Path) -> Path:
    """Create a directory if needed and return it as a Path."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
