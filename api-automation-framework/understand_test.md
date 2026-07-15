# Understanding `tests/test_places.py`

This file automates the Rahul Shetty Academy Place API.

It has two test functions:

```text
test_add_place_success
test_delete_place_success
```

The add test creates places and stores their `place_id`.

The delete test uses the stored `place_id` values and deletes the same places.

Important: this design depends on add tests running before delete tests. Do not
run this file in parallel with `-n auto`.

## Full File Purpose

The file tests this flow:

```text
Read test data
Create place
Validate add response
Save place_id
Delete same place_id
Validate delete response
```

## Imports

```python
from __future__ import annotations
```

This makes type hints lighter and more future-friendly. Python does not need to
evaluate every type hint immediately.

```python
from copy import deepcopy
```

`deepcopy` creates a completely separate copy of a dictionary.

We use it because the base payload has nested data:

```json
{
  "location": {
    "lat": -38.383494,
    "lng": 33.427362
  }
}
```

If we used a normal copy, nested objects like `location` could still be shared.
`deepcopy` avoids accidental changes to the original payload.

```python
from pathlib import Path
```

`Path` is used to represent file paths cleanly:

```python
Path("test_data/json/add_place_payload.json")
```

This is better than plain string paths because it is designed for file-system
work.

```python
from typing import Any
```

`Any` means the value can be any type.

We use it because JSON data can contain:

```text
string
number
object
array
boolean
null
```

So this type is flexible:

```python
dict[str, Any]
```

It means:

```text
dictionary with string keys and any kind of values
```

```python
import pytest
```

Imports pytest so we can use markers and parameterization:

```python
@pytest.mark.regression
@pytest.mark.parametrize(...)
```

```python
from api.place_api import PlaceAPI
```

Imports the API layer class.

The test does not call `requests.post()` directly. Instead, it calls methods
from `PlaceAPI`:

```python
place_api.add_place(payload)
place_api.delete_place(payload)
```

```python
from utils.json_utils import read_json
```

Imports a helper function that reads JSON files and converts them into Python
objects.

Example:

```python
read_json(Path("test_data/json/add_place_payload.json"))
```

returns a Python dictionary.

## Path Constants

```python
ADD_PLACE_PAYLOAD_PATH = Path("test_data/json/add_place_payload.json")
```

This file contains the base request body for Add Place API.

```python
ADD_PLACE_TEST_CASES_PATH = Path("test_data/json/add_place_test_cases.json")
```

This file contains multiple test data rows for parameterization.

Example:

```json
[
  {
    "name": "Frontline house",
    "language": "French-IN",
    "accuracy": 50
  }
]
```

```python
ADD_PLACE_SCHEMA_PATH = Path("schemas/add_place_success_schema.json")
```

This schema validates the Add Place API response.

It checks fields like:

```text
status
place_id
scope
reference
id
```

```python
DELETE_PLACE_SCHEMA_PATH = Path("schemas/delete_place_success_schema.json")
```

This schema validates the Delete Place API response.

It checks that response contains:

```json
{
  "status": "OK"
}
```

## Test Data Loaded Once

```python
ADD_PLACE_TEST_CASES = read_json(ADD_PLACE_TEST_CASES_PATH)
```

This reads all add-place test cases from JSON.

The result is a Python list:

```python
[
    {"name": "Frontline house", "language": "French-IN", "accuracy": 50},
    {"name": "Automation villa", "language": "English-IN", "accuracy": 75},
    {"name": "API learning center", "language": "Hindi-IN", "accuracy": 100},
]
```

This list is used by `pytest.mark.parametrize`.

## Shared Place ID Storage

```python
CREATED_PLACE_IDS: dict[str, str] = {}
```

This is an empty dictionary.

The add test stores created place IDs here.

Example after add tests run:

```python
{
    "Frontline house": "abc123",
    "Automation villa": "def456",
    "API learning center": "ghi789",
}
```

Then the delete test reads from this dictionary.

This is how delete test knows which `place_id` to delete.

## Add Place Test Markers

```python
@pytest.mark.external
```

This marks the test as an external API test.

It means the test calls a real website:

```text
https://rahulshettyacademy.com
```

You can run only external tests with:

```bash
.venv/bin/python -m pytest -m external --env=qa
```

```python
@pytest.mark.regression
```

This marks the test as a regression test.

Regression tests check that existing working functionality is still working
after code changes.

## Deep Explanation Of `parametrize`

```python
@pytest.mark.parametrize(
    "place_data",
    ADD_PLACE_TEST_CASES,
    ids=lambda place_data: str(place_data["name"]),
)
```

`parametrize` means:

```text
Run the same test multiple times with different data.
```

Without parameterization, we might write three separate tests:

```python
def test_add_frontline_house():
    ...

def test_add_automation_villa():
    ...

def test_add_api_learning_center():
    ...
```

That creates duplicate code.

With parameterization, we write one test:

```python
def test_add_place_success(place_api, place_data):
```

and pytest runs it once for each item in `ADD_PLACE_TEST_CASES`.

### First Argument

```python
"place_data"
```

This is the parameter name.

It must match the test function argument:

```python
def test_add_place_success(place_api: PlaceAPI, place_data: dict[str, Any]) -> None:
```

So pytest gives one data row to `place_data` each time it runs the test.

### Second Argument

```python
ADD_PLACE_TEST_CASES
```

This is the list of data rows.

Since it has three rows, pytest creates three test cases:

```text
test_add_place_success[Frontline house]
test_add_place_success[Automation villa]
test_add_place_success[API learning center]
```

### `ids`

```python
ids=lambda place_data: str(place_data["name"])
```

This controls the display name of each generated test.

Without `ids`, pytest may show less readable names.

With `ids`, the report shows meaningful names:

```text
Frontline house
Automation villa
API learning center
```

### What Happens Internally

Pytest transforms this:

```python
@pytest.mark.parametrize("place_data", ADD_PLACE_TEST_CASES)
def test_add_place_success(place_data):
    ...
```

into multiple runs:

```text
Run 1: place_data = {"name": "Frontline house", ...}
Run 2: place_data = {"name": "Automation villa", ...}
Run 3: place_data = {"name": "API learning center", ...}
```

## Add Test Function

```python
def test_add_place_success(place_api: PlaceAPI, place_data: dict[str, Any]) -> None:
```

This is the add-place test.

Because the function name starts with `test_`, pytest executes it.

`place_api` is a fixture. Pytest creates it from:

```text
fixtures/api_fixtures.py
```

`place_data` comes from `parametrize`.

```python
"""Verify a place can be added successfully."""
```

This is the docstring. It explains the purpose of the test.

```python
payload = _add_place_payload(place_data)
```

This creates the final request body.

It starts with the base payload from:

```text
test_data/json/add_place_payload.json
```

Then it updates fields like:

```text
name
language
accuracy
```

from the current parameterized row.

```python
add_schema = read_json(ADD_PLACE_SCHEMA_PATH)
```

This reads the expected response schema for Add Place API.

```python
response = place_api.add_place(payload)
```

This calls the Add Place API.

It goes to:

```text
api/place_api.py
```

and sends:

```text
POST /maps/api/place/add/json?key=qaclick123
```

with the JSON request body.

```python
response.should_have_status(200).should_match_schema(add_schema).should_have_value(
    "status", "OK"
)
```

This validates three things using method chaining:

```text
1. HTTP status code is 200
2. Response matches JSON schema
3. Response field status equals OK
```

Method chaining means one method returns the same response object, so another
method can be called immediately after it.

This:

```python
response.should_have_status(200).should_match_schema(add_schema)
```

is similar to:

```python
response.should_have_status(200)
response.should_match_schema(add_schema)
```

```python
place_id = response.json()["place_id"]
```

This gets the `place_id` from API response.

`response.json()` converts the response body into a Python dictionary.

Example:

```python
{
    "status": "OK",
    "place_id": "abc123",
    "scope": "APP",
    "reference": "...",
    "id": "..."
}
```

So:

```python
response.json()["place_id"]
```

returns:

```text
abc123
```

```python
CREATED_PLACE_IDS[str(place_data["name"])] = place_id
```

This saves the created `place_id`.

The key is the place name.

Example:

```python
CREATED_PLACE_IDS["Frontline house"] = "abc123"
```

The delete test uses the same name to find the correct `place_id`.

```python
print(place_id)
```

This prints the created `place_id` in the terminal.

To see print output, run pytest with `-s`:

```bash
.venv/bin/python -m pytest tests/test_places.py --env=qa -s
```

## Delete Place Test

The delete test uses the same parameterized data.

```python
@pytest.mark.parametrize(
    "place_data",
    ADD_PLACE_TEST_CASES,
    ids=lambda place_data: str(place_data["name"]),
)
```

This means delete test also runs three times:

```text
test_delete_place_success[Frontline house]
test_delete_place_success[Automation villa]
test_delete_place_success[API learning center]
```

```python
def test_delete_place_success(place_api: PlaceAPI, place_data: dict[str, Any]) -> None:
```

This is a separate test function for deleting a place.

It receives:

```text
place_api fixture
place_data from parametrize
```

```python
"""Verify the place created by the add test can be deleted successfully."""
```

This docstring explains that delete depends on the place created by add test.

```python
place_name = str(place_data["name"])
```

This gets the place name from current data row.

Example:

```text
Frontline house
```

```python
place_id = CREATED_PLACE_IDS[place_name]
```

This gets the `place_id` created by the add test.

Example:

```python
place_id = CREATED_PLACE_IDS["Frontline house"]
```

If add test did not run first, this line will fail with `KeyError`.

That is why this design depends on test order.

```python
delete_schema = read_json(DELETE_PLACE_SCHEMA_PATH)
```

This reads the expected response schema for Delete Place API.

```python
delete_response = place_api.delete_place({"place_id": place_id})
```

This calls the Delete Place API.

The request body is:

```json
{
  "place_id": "abc123"
}
```

The API endpoint is:

```text
POST /maps/api/place/delete/json?key=qaclick123
```

```python
delete_response.should_have_status(200).should_match_schema(delete_schema).should_have_value(
    "status", "OK"
)
```

This validates:

```text
1. Delete response status code is 200
2. Delete response matches schema
3. Delete response has status = OK
```

## Helper Function

```python
def _add_place_payload(place_data: dict[str, Any]) -> dict[str, Any]:
```

This is a helper function.

The underscore `_` means it is intended for internal use inside this file.

```python
"""Return a request payload by applying test-case values to the base payload."""
```

This explains what the helper does.

```python
payload = deepcopy(read_json(ADD_PLACE_PAYLOAD_PATH))
```

This reads the base payload from JSON and creates a deep copy.

Base payload contains common fields like:

```text
location
phone_number
address
types
website
```

```python
payload.update(place_data)
```

This updates the base payload with current test data.

Example:

Base payload has:

```json
{
  "name": "Frontline house",
  "accuracy": 50,
  "language": "French-IN"
}
```

If current test case has:

```json
{
  "name": "Automation villa",
  "accuracy": 75,
  "language": "English-IN"
}
```

then `payload.update(place_data)` replaces those values.

```python
return payload
```

Returns the final request body used by Add Place API.

## Complete Execution Flow

When you run:

```bash
.venv/bin/python -m pytest tests/test_places.py --env=qa -s
```

pytest executes:

```text
test_add_place_success[Frontline house]
  -> add place
  -> save place_id for Frontline house

test_add_place_success[Automation villa]
  -> add place
  -> save place_id for Automation villa

test_add_place_success[API learning center]
  -> add place
  -> save place_id for API learning center

test_delete_place_success[Frontline house]
  -> read saved place_id for Frontline house
  -> delete that place_id

test_delete_place_success[Automation villa]
  -> read saved place_id for Automation villa
  -> delete that place_id

test_delete_place_success[API learning center]
  -> read saved place_id for API learning center
  -> delete that place_id
```

## Important Framework Note

This design uses shared memory:

```python
CREATED_PLACE_IDS
```

That means delete tests depend on add tests.

This is useful for learning how one API response can feed another API request.

But for large professional test suites, independent tests are usually safer.

For this current learning goal, the design is correct because the requirement is:

```text
Add a place, get its place_id, and delete the same place_id in a separate delete test.
```

