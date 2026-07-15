"""Place API resource methods for Rahul Shetty Academy sample API."""

from __future__ import annotations

from typing import Any

from core.api_client import APIClient
from core.response_wrapper import ResponseWrapper


class PlaceAPI:
    """High-level operations for place endpoints."""

    ADD_PLACE_ENDPOINT = "/maps/api/place/add/json"
    DELETE_PLACE_ENDPOINT = "/maps/api/place/delete/json"

    def __init__(self, client: APIClient, api_key: str) -> None:
        """Initialize the API with an injected API client."""
        self._client = client
        self._api_key = api_key

    def add_place(self, payload: dict[str, Any]) -> ResponseWrapper:
        """Add a new place."""
        return self._client.post(
            self.ADD_PLACE_ENDPOINT,
            params={"key": self._api_key},
            json=payload,
        )
    
    def get_place(self, place_id: str) -> ResponseWrapper:
        """Get a place by its ID."""
        return self._client.get(
            "/maps/api/place/get/json",
            params={"key": self._api_key, "place_id": place_id},
        )

    def delete_place(self, payload: dict[str, Any]) -> ResponseWrapper:
        """Delete a place."""
        return self._client.post(
            self.DELETE_PLACE_ENDPOINT,
            params={"key": self._api_key},
            json=payload,
        )