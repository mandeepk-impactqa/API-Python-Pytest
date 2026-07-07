"""User API resource methods."""

from __future__ import annotations

from typing import Any

from core.api_client import APIClient
from core.response_wrapper import ResponseWrapper


class UserAPI:
    """High-level operations for user endpoints."""

    def __init__(self, client: APIClient) -> None:
        """Initialize the API with an injected API client."""
        self._client = client

    def list_users(self, page: int = 1) -> ResponseWrapper:
        """Return users for a page."""
        return self._client.get("/api/users", params={"page": page})

    def get_user(self, user_id: int) -> ResponseWrapper:
        """Return one user by ID."""
        return self._client.get("/api/users/{user_id}", path_params={"user_id": user_id})

    def create_user(self, payload: dict[str, Any]) -> ResponseWrapper:
        """Create a user."""
        return self._client.post("/api/users", json=payload)

    def update_user(self, user_id: int, payload: dict[str, Any]) -> ResponseWrapper:
        """Replace a user."""
        return self._client.put(
            "/api/users/{user_id}", path_params={"user_id": user_id}, json=payload
        )

    def patch_user(self, user_id: int, payload: dict[str, Any]) -> ResponseWrapper:
        """Partially update a user."""
        return self._client.patch(
            "/api/users/{user_id}", path_params={"user_id": user_id}, json=payload
        )

    def delete_user(self, user_id: int) -> ResponseWrapper:
        """Delete a user."""
        return self._client.delete("/api/users/{user_id}", path_params={"user_id": user_id})
