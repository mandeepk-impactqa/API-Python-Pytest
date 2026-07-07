"""Negative API behavior tests."""

from __future__ import annotations

import pytest

from api.user_api import UserAPI


@pytest.mark.negative
def test_unknown_user_returns_not_found(user_api: UserAPI) -> None:
    """Verify unknown user IDs return a 404 response."""
    response = user_api.get_user(23)

    response.should_have_status(404)


@pytest.mark.negative
def test_delete_user_is_idempotent_contract(user_api: UserAPI) -> None:
    """Verify deleting a user returns the documented no-content response."""
    response = user_api.delete_user(2)

    response.should_have_status(204)
