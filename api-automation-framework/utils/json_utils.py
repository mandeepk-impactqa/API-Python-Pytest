"""JSON file loading and writing helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> Any:
    """Read JSON from disk and return the parsed content."""
    with Path(path).open(encoding="utf-8") as file:
        return json.load(file)


def write_json(path: str | Path, data: Any) -> None:
    """Write JSON content to disk with stable formatting."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=True)
        file.write("\n")
