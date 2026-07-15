"""Place endpoint tests."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from api.place_api import PlaceAPI
from utils.json_utils import read_json

ADD_PLACE_PAYLOAD_PATH = Path("test_data/json/add_place_payload.json")
ADD_PLACE_TEST_CASES_PATH = Path("test_data/json/add_place_test_cases.json")
ADD_PLACE_SCHEMA_PATH = Path("schemas/add_place_success_schema.json")
GET_PLACE_SCHEMA_PATH = Path("schemas/get_place_by_id_success_schema.json")
DELETE_PLACE_SCHEMA_PATH = Path("schemas/delete_place_success_schema.json")
ADD_PLACE_TEST_CASES = read_json(ADD_PLACE_TEST_CASES_PATH)
CREATED_PLACE_IDS: dict[str, str] = {}


@pytest.mark.external
@pytest.mark.regression
@pytest.mark.parametrize(
    "place_data",
    ADD_PLACE_TEST_CASES,
    ids=lambda place_data: str(place_data["name"]),
)
def test_add_place_success(place_api: PlaceAPI, place_data: dict[str, Any]) -> None:
    """Verify a place can be added successfully."""
    payload = _add_place_payload(place_data)
    add_schema = read_json(ADD_PLACE_SCHEMA_PATH)

    response = place_api.add_place(payload)

    response.should_have_status(200).should_match_schema(add_schema).should_have_value(
        "status", "OK"
    )
    place_id = response.json()["place_id"]
    CREATED_PLACE_IDS[str(place_data["name"])] = place_id
    print(place_id)


@pytest.mark.external
@pytest.mark.regression
@pytest.mark.parametrize(
    "place_data",
    ADD_PLACE_TEST_CASES,
    ids=lambda place_data: str(place_data["name"]),
)
def test_get_place_By_Id_success(place_api: PlaceAPI, place_data: dict[str, Any]) -> None:
    """Verify a place can be retrieved successfully."""
    place_name = str(place_data["name"])
    place_id = CREATED_PLACE_IDS[place_name]
    get_schema = read_json(GET_PLACE_SCHEMA_PATH)
    response = place_api.get_place(place_id)
    response.should_have_status(200).should_match_schema(get_schema).should_have_value(
        "name", place_name
    )


@pytest.mark.external
@pytest.mark.regression
@pytest.mark.parametrize(
    "place_data",
    ADD_PLACE_TEST_CASES,
    ids=lambda place_data: str(place_data["name"]),
)
def test_delete_place_success(place_api: PlaceAPI, place_data: dict[str, Any]) -> None:
    """Verify the place created by the add test can be deleted successfully."""
    place_name = str(place_data["name"])
    place_id = CREATED_PLACE_IDS[place_name]
    delete_schema = read_json(DELETE_PLACE_SCHEMA_PATH)

    delete_response = place_api.delete_place({"place_id": place_id})

    delete_response.should_have_status(200).should_match_schema(delete_schema).should_have_value(
        "status", "OK"
    )


def _add_place_payload(place_data: dict[str, Any]) -> dict[str, Any]:
    """Return a request payload by applying test-case values to the base payload."""
    payload = deepcopy(read_json(ADD_PLACE_PAYLOAD_PATH))
    payload.update(place_data)
    return payload
