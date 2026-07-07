"""Product API resource methods."""

from __future__ import annotations

from typing import Any

from core.api_client import APIClient
from core.response_wrapper import ResponseWrapper


class ProductAPI:
    """High-level operations for product-like endpoints."""

    def __init__(self, client: APIClient) -> None:
        """Initialize the API with an injected API client."""
        self._client = client

    def list_products(self, page: int = 1) -> ResponseWrapper:
        """Return available products."""
        return self._client.get("/api/unknown", params={"page": page})

    def get_product(self, product_id: int) -> ResponseWrapper:
        """Return a product by ID."""
        return self._client.get("/api/unknown/{product_id}", path_params={"product_id": product_id})

    def create_product(self, payload: dict[str, Any]) -> ResponseWrapper:
        """Create a product against a configurable product endpoint."""
        return self._client.post("/api/products", json=payload)
