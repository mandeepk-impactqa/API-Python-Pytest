"""Fluent request builder used by API layer classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RequestSpec:
    """Complete request specification consumed by APIClient."""

    method: str
    base_url: str
    endpoint: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    path_params: dict[str, Any] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    json_body: Any | None = None
    data: dict[str, Any] | None = None
    files: dict[str, Any] | None = None
    timeout: float | None = None
    auth: Any | None = None


class RequestBuilder:
    """Build request specifications with a fluent, chainable API."""

    def __init__(self) -> None:
        """Initialize an empty request builder."""
        self._method = "GET"
        self._base_url = ""
        self._endpoint = ""
        self._headers: dict[str, str] = {}
        self._params: dict[str, Any] = {}
        self._path_params: dict[str, Any] = {}
        self._cookies: dict[str, str] = {}
        self._json_body: Any | None = None
        self._data: dict[str, Any] | None = None
        self._files: dict[str, Any] | None = None
        self._timeout: float | None = None
        self._auth: Any | None = None

    def method(self, method: str) -> "RequestBuilder":
        """Set the HTTP method."""
        self._method = method.upper()
        return self

    def base_url(self, base_url: str) -> "RequestBuilder":
        """Set the base URL."""
        self._base_url = base_url.rstrip("/")
        return self

    def endpoint(self, endpoint: str) -> "RequestBuilder":
        """Set the endpoint path."""
        self._endpoint = endpoint
        return self

    def headers(self, headers: dict[str, str] | None) -> "RequestBuilder":
        """Merge request headers."""
        self._headers.update(headers or {})
        return self

    def params(self, params: dict[str, Any] | None) -> "RequestBuilder":
        """Merge query parameters."""
        self._params.update(params or {})
        return self

    def path_params(self, path_params: dict[str, Any] | None) -> "RequestBuilder":
        """Merge path parameters used to format endpoint templates."""
        self._path_params.update(path_params or {})
        return self

    def cookies(self, cookies: dict[str, str] | None) -> "RequestBuilder":
        """Merge request cookies."""
        self._cookies.update(cookies or {})
        return self

    def body(self, body: Any | None) -> "RequestBuilder":
        """Set a JSON request body."""
        self._json_body = body
        return self

    def form(self, data: dict[str, Any] | None) -> "RequestBuilder":
        """Set form data."""
        self._data = data
        return self

    def multipart(self, files: dict[str, Any] | None) -> "RequestBuilder":
        """Set multipart file payload."""
        self._files = files
        return self

    def timeout(self, timeout: float | None) -> "RequestBuilder":
        """Set a request-specific timeout."""
        self._timeout = timeout
        return self

    def auth(self, auth: Any | None) -> "RequestBuilder":
        """Set request authentication."""
        self._auth = auth
        return self

    def build(self) -> RequestSpec:
        """Build and return an immutable request specification."""
        return RequestSpec(
            method=self._method,
            base_url=self._base_url,
            endpoint=self._endpoint,
            headers=dict(self._headers),
            params=dict(self._params),
            path_params=dict(self._path_params),
            cookies=dict(self._cookies),
            json_body=self._json_body,
            data=self._data,
            files=self._files,
            timeout=self._timeout,
            auth=self._auth,
        )
