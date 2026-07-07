"""Authentication endpoint tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from api.auth_api import AuthAPI
from utils.file_utils import read_yaml
from utils.json_utils import read_json


@pytest.mark.smoke
def test_login_success(auth_api: AuthAPI) -> None:
    """Verify valid credentials produce a token and match the response schema."""
    login_data = read_yaml(Path("test_data/yaml/login.yaml"))["valid_user"]
    schema = read_json(Path("schemas/login_success_schema.json"))

    response = auth_api.login(login_data["email"], login_data["password"])

    response.should_have_status(200).should_match_schema(schema).should_have_response_time(5.0)


@pytest.mark.negative
def test_login_requires_password(auth_api: AuthAPI) -> None:
    """Verify login fails when the password is omitted."""
    response = auth_api.login("peter@klaven", "")

    response.should_have_status(400).should_have_key("error")
