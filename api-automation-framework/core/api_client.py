"""Reusable requests-based API client used by all API layer classes."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import urljoin

import allure
import requests
from requests import Session
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import RequestException, Timeout

from core.config import FrameworkConfig
from core.exceptions import APIClientError
from core.logger import get_logger, sanitize_mapping, to_pretty_json
from core.request_builder import RequestBuilder, RequestSpec
from core.response_wrapper import ResponseWrapper
from core.retry import create_retry_adapter


class APIClient:
    """HTTP client with session reuse, retry, logging, and response wrapping."""

    def __init__(self, config: FrameworkConfig, session: Session | None = None) -> None:
        """Create an API client for one test environment."""
        self._config = config
        self._session = session or requests.Session()
        self._logger = get_logger(self.__class__.__name__)
        adapter = create_retry_adapter(config.retry_total, config.retry_backoff_factor)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def get(self, endpoint: str, **kwargs: Any) -> ResponseWrapper:
        """Send a GET request."""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> ResponseWrapper:
        """Send a POST request."""
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> ResponseWrapper:
        """Send a PUT request."""
        return self.request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs: Any) -> ResponseWrapper:
        """Send a PATCH request."""
        return self.request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> ResponseWrapper:
        """Send a DELETE request."""
        return self.request("DELETE", endpoint, **kwargs)

    def options(self, endpoint: str, **kwargs: Any) -> ResponseWrapper:
        """Send an OPTIONS request."""
        return self.request("OPTIONS", endpoint, **kwargs)

    def head(self, endpoint: str, **kwargs: Any) -> ResponseWrapper:
        """Send a HEAD request."""
        return self.request("HEAD", endpoint, **kwargs)

    def request(self, method: str, endpoint: str, **kwargs: Any) -> ResponseWrapper:
        """Build and execute an HTTP request."""
        spec = (
            RequestBuilder()
            .method(method)
            .base_url(kwargs.pop("base_url", self._config.base_url))
            .endpoint(endpoint)
            .headers(kwargs.pop("headers", None))
            .params(kwargs.pop("params", None))
            .path_params(kwargs.pop("path_params", None))
            .cookies(kwargs.pop("cookies", None))
            .body(kwargs.pop("json", None))
            .form(kwargs.pop("data", None))
            .multipart(kwargs.pop("files", None))
            .timeout(kwargs.pop("timeout", self._config.timeout_seconds))
            .auth(kwargs.pop("auth", None))
            .build()
        )
        if kwargs:
            unexpected = ", ".join(sorted(kwargs))
            raise APIClientError(f"Unsupported request arguments: {unexpected}")
        return self.send(spec)

    def send(self, spec: RequestSpec) -> ResponseWrapper:
        """Execute a request specification and return a wrapped response."""
        url = self._build_url(spec.base_url, spec.endpoint, spec.path_params)
        self._log_request(spec, url)
        try:
            response = self._session.request(
                method=spec.method,
                url=url,
                params=spec.params,
                headers=spec.headers,
                cookies=spec.cookies,
                json=spec.json_body,
                data=spec.data,
                files=spec.files,
                timeout=spec.timeout or self._config.timeout_seconds,
                verify=self._config.verify_ssl,
                auth=spec.auth,
            )
        except (Timeout, RequestsConnectionError) as exc:
            raise APIClientError(f"{spec.method} {url} failed due to network error: {exc}") from exc
        except RequestException as exc:
            raise APIClientError(f"{spec.method} {url} failed: {exc}") from exc

        wrapper = ResponseWrapper(response)
        self._log_response(wrapper)
        self._attach_allure(spec, url, wrapper)
        return wrapper

    @staticmethod
    def _build_url(base_url: str, endpoint: str, path_params: Mapping[str, Any]) -> str:
        """Build a final URL from base URL, endpoint, and path parameters."""
        formatted_endpoint = endpoint.format(**path_params) if path_params else endpoint
        return urljoin(f"{base_url.rstrip('/')}/", formatted_endpoint.lstrip("/"))

    def _log_request(self, spec: RequestSpec, url: str) -> None:
        """Log outgoing request details."""
        self._logger.info(
            "REQUEST %s %s headers=%s params=%s body=%s",
            spec.method,
            url,
            to_pretty_json(sanitize_mapping(spec.headers)),
            to_pretty_json(spec.params),
            to_pretty_json(spec.json_body or spec.data or {}),
        )

    def _log_response(self, response: ResponseWrapper) -> None:
        """Log incoming response details."""
        self._logger.info(
            "RESPONSE status=%s time=%.3fs headers=%s body=%s",
            response.status_code,
            response.elapsed_time,
            to_pretty_json(sanitize_mapping(dict(response.headers))),
            response.text[:5000],
        )

    @staticmethod
    def _attach_allure(spec: RequestSpec, url: str, response: ResponseWrapper) -> None:
        """Attach request and response details to Allure when available."""
        try:
            allure.attach(url, "Request URL", allure.attachment_type.TEXT)
            allure.attach(
                to_pretty_json(sanitize_mapping(spec.headers)),
                "Request Headers",
                allure.attachment_type.JSON,
            )
            allure.attach(
                to_pretty_json(spec.json_body or spec.data or {}),
                "Request Body",
                allure.attachment_type.JSON,
            )
            allure.attach(
                to_pretty_json(sanitize_mapping(dict(response.headers))),
                "Response Headers",
                allure.attachment_type.JSON,
            )
            allure.attach(response.text, "Response Body", allure.attachment_type.TEXT)
            allure.attach(
                f"{response.elapsed_time:.3f}s", "Response Time", allure.attachment_type.TEXT
            )
        except RuntimeError:
            return
