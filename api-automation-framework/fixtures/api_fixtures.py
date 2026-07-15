"""Reusable API resource fixtures."""

from __future__ import annotations

import pytest
import requests

from api.place_api import PlaceAPI
from core.api_client import APIClient
from core.config import FrameworkConfig
from core.exceptions import ConfigurationError


@pytest.fixture(scope="session")
def api_client(config: FrameworkConfig) -> APIClient:
    """Return a session-scoped API client."""
    session = requests.Session()
    return APIClient(config=config, session=session)


@pytest.fixture(scope="session")
def place_api(api_client: APIClient, config: FrameworkConfig) -> PlaceAPI:
    """Return the place API resource."""
    if not config.api_key:
        raise ConfigurationError("API_KEY is required for Place API requests.")
    return PlaceAPI(api_client, api_key=config.api_key)
