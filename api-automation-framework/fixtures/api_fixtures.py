"""Reusable API resource fixtures."""

from __future__ import annotations

import pytest
import requests

from api.auth_api import AuthAPI
from api.product_api import ProductAPI
from api.user_api import UserAPI
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
def auth_api(api_client: APIClient) -> AuthAPI:
    """Return the authentication API resource."""
    return AuthAPI(api_client)


@pytest.fixture(scope="session")
def user_api(api_client: APIClient) -> UserAPI:
    """Return the user API resource."""
    return UserAPI(api_client)


@pytest.fixture(scope="session")
def product_api(api_client: APIClient) -> ProductAPI:
    """Return the product API resource."""
    return ProductAPI(api_client)
