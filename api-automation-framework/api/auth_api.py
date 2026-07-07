"""Authentication API resource methods."""

from __future__ import annotations

from core.api_client import APIClient
from core.response_wrapper import ResponseWrapper


class AuthAPI:
    """High-level operations for authentication endpoints."""

    def __init__(self, client: APIClient) -> None:
        """Initialize the API with an injected API client."""
        self._client = client

    def login(self, email: str, password: str) -> ResponseWrapper:
        """Authenticate a user with email and password."""
        return self._client.post("/api/login", json={"email": email, "password": password})

    def register(self, email: str, password: str) -> ResponseWrapper:
        """Register a user with email and password."""
        return self._client.post("/api/register", json={"email": email, "password": password})
