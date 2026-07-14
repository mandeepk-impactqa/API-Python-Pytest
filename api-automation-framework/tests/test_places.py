"""Place endpoint tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from api.place_api import PlaceAPI
from utils.json_utils import read_json


@pytest.mark.external
@pytest.mark.regression
def test_add_place_success(place_api: PlaceAPI) -> None:
    """Verify a place can be added and the response matches the schema."""
    payload = read_json(Path("test_data/json/add_place_payload.json"))
    schema = read_json(Path("schemas/add_place_success_schema.json"))

    response = place_api.add_place(payload)

    response.should_have_status(200).should_match_schema(schema).should_have_value("status", "OK")
