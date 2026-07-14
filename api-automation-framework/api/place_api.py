"""Place API resource methods for Rahul Shetty Academy sample API."""

from __future__ import annotations

from typing import Any

from core.api_client import APIClient
from core.response_wrapper import ResponseWrapper


class PlaceAPI:
    """High-level operations for place endpoints."""

    def __init__(self, client: APIClient, api_key: str) -> None:
        """Initialize the API with an injected API client."""
        self._client = client
        self._api_key = api_key

    def add_place(self, payload: dict[str, Any]) -> ResponseWrapper:
        """Add a new place."""
        return self._client.post(
            "/maps/api/place/add/json",
            params={"key": self._api_key},
            json=payload,
        )
