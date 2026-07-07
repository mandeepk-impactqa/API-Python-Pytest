"""User endpoint tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from api.user_api import UserAPI
from utils.file_utils import read_csv
from utils.json_utils import read_json
from utils.random_data import user_payload


@pytest.mark.smoke
def test_list_users_matches_schema(user_api: UserAPI) -> None:
    """Verify users can be listed and match the configured schema."""
    schema = read_json(Path("schemas/user_list_schema.json"))

    response = user_api.list_users(page=1)

    response.should_have_status(200).should_match_schema(schema).should_have_response_time(5.0)


@pytest.mark.regression
@pytest.mark.parametrize("user_id", [1, 2])
def test_get_user_by_id(user_api: UserAPI, user_id: int) -> None:
    """Verify individual users can be fetched by ID."""
    response = user_api.get_user(user_id)

    response.should_have_status(200).should_have_key("data")


@pytest.mark.regression
def test_create_user_from_dynamic_payload(user_api: UserAPI) -> None:
    """Verify creating a user from faker-generated data."""
    payload = user_payload()

    response = user_api.create_user(payload)

    response.should_have_status(201).should_have_value("name", payload["name"])


@pytest.mark.regression
@pytest.mark.parametrize("row", read_csv(Path("test_data/csv/users.csv")))
def test_create_user_from_csv(user_api: UserAPI, row: dict[str, str]) -> None:
    """Verify creating users using CSV-driven parameterization."""
    response = user_api.create_user(row)

    response.should_have_status(201).should_have_value("job", row["job"])
