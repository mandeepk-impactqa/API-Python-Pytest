"""Reusable API resource fixtures."""

from __future__ import annotations

import pytest
import requests

from api.place_api import PlaceAPI
from core.api_client import APIClient
from core.auth_manager import AuthManager
from core.config import FrameworkConfig


@pytest.fixture(scope="session")
def api_client(config: FrameworkConfig) -> APIClient:
    """Return a session-scoped API client with optional API key headers."""
    session = requests.Session()
    auth_manager = AuthManager(config)
    if config.api_key:
        session.headers.update(auth_manager.api_key_headers())
    return APIClient(config=config, session=session)


@pytest.fixture(scope="session")
def place_api(api_client: APIClient, config: FrameworkConfig) -> PlaceAPI:
    """Return the place API resource."""
    return PlaceAPI(api_client, api_key=config.api_key or "")
