"""Authentication-related pytest fixtures."""

from __future__ import annotations

import pytest

from api.auth_api import AuthAPI


@pytest.fixture(scope="session")
def bearer_token(auth_api: AuthAPI) -> str:
    """Return a bearer token acquired through the configured login endpoint."""
    response = auth_api.login("eve.holt@reqres.in", "cityslicka").should_have_status(200)
    token = response.json().get("token")
    if not isinstance(token, str) or not token:
        raise AssertionError("Login response did not include a bearer token.")
    return token
