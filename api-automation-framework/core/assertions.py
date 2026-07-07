"""Reusable assertion helpers for API response validation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from jsonschema import ValidationError, validate

from core.exceptions import ResponseValidationError


def assert_status(actual: int, expected: int | Sequence[int]) -> None:
    """Assert that a status code matches one expected value or a collection."""
    expected_values = {expected} if isinstance(expected, int) else set(expected)
    if actual not in expected_values:
        raise ResponseValidationError(f"Expected status {expected_values}, got {actual}.")


def assert_schema(payload: Any, schema: Mapping[str, Any]) -> None:
    """Assert that a JSON payload matches a JSON schema."""
    try:
        validate(instance=payload, schema=dict(schema))
    except ValidationError as exc:
        raise ResponseValidationError(f"Schema validation failed: {exc.message}") from exc


def assert_key(payload: Mapping[str, Any], key: str) -> None:
    """Assert that a mapping contains a key."""
    if key not in payload:
        raise ResponseValidationError(f"Expected key '{key}' was not found.")


def assert_value(payload: Mapping[str, Any], key: str, expected: Any) -> None:
    """Assert that a mapping key has an expected value."""
    assert_key(payload, key)
    actual = payload[key]
    if actual != expected:
        raise ResponseValidationError(f"Expected {key}={expected!r}, got {actual!r}.")


def assert_cookie(cookies: Mapping[str, Any], name: str) -> None:
    """Assert that a cookie exists."""
    if name not in cookies:
        raise ResponseValidationError(f"Expected cookie '{name}' was not found.")


def assert_header(headers: Mapping[str, Any], name: str) -> None:
    """Assert that a header exists, case-insensitively."""
    header_names = {header.lower() for header in headers}
    if name.lower() not in header_names:
        raise ResponseValidationError(f"Expected header '{name}' was not found.")


def assert_not_null(value: Any, field_name: str = "value") -> None:
    """Assert that a value is not None."""
    if value is None:
        raise ResponseValidationError(f"Expected {field_name} to be non-null.")


def assert_list_size(values: Sequence[Any], expected_size: int) -> None:
    """Assert that a sequence has the expected size."""
    actual_size = len(values)
    if actual_size != expected_size:
        raise ResponseValidationError(f"Expected list size {expected_size}, got {actual_size}.")
