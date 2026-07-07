"""Local demo API server used for deterministic framework smoke tests."""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest

from core.config import FrameworkConfig
from core.logger import get_logger


class DemoAPIHandler(BaseHTTPRequestHandler):
    """Small HTTP API that mirrors the sample contracts used by tests."""

    server_version = "DemoAPI/1.0"

    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/api/users":
            page = int(parse_qs(parsed_path.query).get("page", ["1"])[0])
            self._write_json(200, _user_list(page))
            return
        if parsed_path.path.startswith("/api/users/"):
            user_id = _path_id(parsed_path.path)
            user = _user_by_id(user_id)
            self._write_json(200, {"data": user}) if user else self._write_json(404, {})
            return
        if parsed_path.path == "/api/unknown":
            self._write_json(200, _product_list())
            return
        if parsed_path.path.startswith("/api/unknown/"):
            product_id = _path_id(parsed_path.path)
            product = _product_by_id(product_id)
            self._write_json(200, {"data": product}) if product else self._write_json(404, {})
            return
        self._write_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        """Handle POST requests."""
        payload = self._read_json()
        if self.path == "/api/login":
            if (
                payload.get("email") == "eve.holt@reqres.in"
                and payload.get("password") == "cityslicka"
            ):
                self._write_json(200, {"token": "demo-token"})
                return
            self._write_json(400, {"error": "Missing password"})
            return
        if self.path == "/api/register":
            self._write_json(200, {"id": 4, "token": "demo-token"})
            return
        if self.path in {"/api/users", "/api/products"}:
            self._write_json(201, {**payload, "id": "101", "createdAt": "2026-07-07T00:00:00Z"})
            return
        self._write_json(404, {"error": "not_found"})

    def do_PUT(self) -> None:
        """Handle PUT requests."""
        payload = self._read_json()
        self._write_json(200, {**payload, "updatedAt": "2026-07-07T00:00:00Z"})

    def do_PATCH(self) -> None:
        """Handle PATCH requests."""
        payload = self._read_json()
        self._write_json(200, {**payload, "updatedAt": "2026-07-07T00:00:00Z"})

    def do_DELETE(self) -> None:
        """Handle DELETE requests."""
        if self.path.startswith("/api/users/"):
            self.send_response(204)
            self.end_headers()
            return
        self._write_json(404, {"error": "not_found"})

    def log_message(self, format: str, *args: Any) -> None:
        """Route server logs through the framework logger."""
        get_logger("demo_api").info(format, *args)

    def _read_json(self) -> dict[str, Any]:
        """Read a JSON request body."""
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        body = self.rfile.read(length).decode("utf-8")
        payload = json.loads(body)
        return payload if isinstance(payload, dict) else {}

    def _write_json(self, status_code: int, payload: dict[str, Any]) -> None:
        """Write a JSON response."""
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


@pytest.fixture(scope="session", autouse=True)
def demo_api_server(config: FrameworkConfig) -> Iterator[None]:
    """Start the local demo API when the configured base URL points to localhost."""
    parsed_url = urlparse(config.base_url)
    if parsed_url.hostname not in {"127.0.0.1", "localhost"}:
        yield
        return

    host = parsed_url.hostname or "127.0.0.1"
    port = parsed_url.port or 80
    server = ThreadingHTTPServer((host, port), DemoAPIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    get_logger("demo_api").info("Started local demo API at %s", config.base_url)
    yield
    server.shutdown()
    server.server_close()


def _path_id(path: str) -> int:
    """Return the integer ID from the end of a path."""
    return int(path.rstrip("/").split("/")[-1])


def _user_by_id(user_id: int) -> dict[str, Any] | None:
    """Return a demo user by ID."""
    users = {user["id"]: user for user in _user_list(page=1)["data"]}
    return users.get(user_id)


def _user_list(page: int) -> dict[str, Any]:
    """Return a reqres-compatible demo user list."""
    users = [
        {
            "id": 1,
            "email": "george.bluth@example.com",
            "first_name": "George",
            "last_name": "Bluth",
            "avatar": "https://example.test/avatar/1.png",
        },
        {
            "id": 2,
            "email": "janet.weaver@example.com",
            "first_name": "Janet",
            "last_name": "Weaver",
            "avatar": "https://example.test/avatar/2.png",
        },
    ]
    return {"page": page, "per_page": 2, "total": 2, "total_pages": 1, "data": users}


def _product_by_id(product_id: int) -> dict[str, Any] | None:
    """Return a demo product by ID."""
    products = {product["id"]: product for product in _product_list()["data"]}
    return products.get(product_id)


def _product_list() -> dict[str, Any]:
    """Return a reqres-compatible demo product list."""
    return {
        "page": 1,
        "per_page": 2,
        "total": 2,
        "total_pages": 1,
        "data": [
            {
                "id": 1,
                "name": "cerulean",
                "year": 2000,
                "color": "#98B2D1",
                "pantone_value": "15-4020",
            },
            {
                "id": 2,
                "name": "fuchsia rose",
                "year": 2001,
                "color": "#C74375",
                "pantone_value": "17-2031",
            },
        ],
    }
