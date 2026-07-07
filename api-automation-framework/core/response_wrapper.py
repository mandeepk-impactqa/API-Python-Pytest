"""Wrapper around requests.Response with contract assertion helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from requests import Response

from core.assertions import assert_key, assert_schema, assert_status, assert_value
from core.exceptions import ResponseValidationError


class ResponseWrapper:
    """Expose response data and fluent validation helpers."""

    def __init__(self, response: Response) -> None:
        """Wrap a requests response."""
        self._response = response

    @property
    def status_code(self) -> int:
        """Return the HTTP status code."""
        return self._response.status_code

    @property
    def headers(self) -> Mapping[str, str]:
        """Return response headers."""
        return self._response.headers

    @property
    def cookies(self) -> Mapping[str, str]:
        """Return response cookies."""
        return self._response.cookies.get_dict()

    @property
    def elapsed_time(self) -> float:
        """Return response elapsed time in seconds."""
        return self._response.elapsed.total_seconds()

    @property
    def text(self) -> str:
        """Return response text."""
        return self._response.text

    @property
    def raw_response(self) -> Response:
        """Return the underlying requests response."""
        return self._response

    def json(self) -> Any:
        """Return parsed JSON response content."""
        return self._response.json()

    def should_have_status(self, expected: int | Sequence[int]) -> "ResponseWrapper":
        """Assert the response has an expected status code."""
        assert_status(self.status_code, expected)
        return self

    def should_have_key(self, key: str) -> "ResponseWrapper":
        """Assert the response JSON object contains a key."""
        payload = self.json()
        if not isinstance(payload, dict):
            raise ResponseValidationError("Response JSON is not an object.")
        assert_key(payload, key)
        return self

    def should_have_value(self, key: str, expected: Any) -> "ResponseWrapper":
        """Assert the response JSON object contains an expected key value."""
        payload = self.json()
        if not isinstance(payload, dict):
            raise ResponseValidationError("Response JSON is not an object.")
        assert_value(payload, key, expected)
        return self

    def should_match_schema(self, schema: Mapping[str, Any]) -> "ResponseWrapper":
        """Assert the response JSON matches a JSON schema."""
        assert_schema(self.json(), schema)
        return self

    def should_have_response_time(self, max_seconds: float) -> "ResponseWrapper":
        """Assert response time is less than or equal to a limit."""
        if self.elapsed_time > max_seconds:
            raise ResponseValidationError(
                f"Expected response time <= {max_seconds}s, got {self.elapsed_time:.3f}s."
            )
        return self
