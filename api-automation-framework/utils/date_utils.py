"""Date and time helpers for payload generation and assertions."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""
    return datetime.now(UTC).isoformat()


def utc_date_after(days: int) -> str:
    """Return a future or past UTC date in ISO-8601 format."""
    return (datetime.now(UTC) + timedelta(days=days)).date().isoformat()
