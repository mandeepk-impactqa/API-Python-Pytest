# The Framework, Cinematic Edition

Imagine this framework as a film set.

The story is simple:

```text
A place is born.
The place receives an identity.
That identity is remembered.
Then the same place is removed.
Finally, the report tells us whether the mission succeeded.
```

In automation language:

```text
Add Place API
  -> capture place_id
  -> Delete Place API using same place_id
  -> validate responses
  -> generate reports
```

## Opening Shot: The Project

The camera opens on the project folder:

```text
api-automation-framework/
```

This is not just a folder. It is the city where every part of the framework has
its own job.

```text
config/       Decides which world the tests run against
test_data/    Gives the story its input data
schemas/      Defines what a correct response must look like
api/          Knows the API resources and endpoints
core/         Runs the actual HTTP machinery
fixtures/     Prepares objects before the test starts
tests/        Directs the actual test scenes
reports/      Shows the final result
```

## Scene 1: The Environment Is Chosen

The first decision is:

```text
Where are we sending the API request?
```

That answer lives in:

```text
config/qa.env
```

Inside it:

```text
BASE_URL=https://rahulshettyacademy.com
API_KEY=qaclick123
```

This tells the framework:

```text
Use Rahul Shetty Academy as the base API.
Use qaclick123 as the API key.
```

When you run:

```bash
.venv/bin/python -m pytest tests/test_places.py --env=qa
```

the framework loads `qa.env`.

So the test does not hardcode the base URL inside the test file.

That is good framework design.

## Scene 2: Pytest Calls The Cast

Before the test begins, pytest looks at the test function:

```python
def test_add_place_success(place_api: PlaceAPI, place_data: dict[str, Any]) -> None:
```

Pytest sees:

```text
place_api
```

and asks:

```text
Who can create place_api?
```

The answer is in:

```text
fixtures/api_fixtures.py
```

There, this fixture creates the API object:

```python
def place_api(api_client: APIClient, config: FrameworkConfig) -> PlaceAPI:
    if not config.api_key:
        raise ConfigurationError("API_KEY is required for Place API requests.")
    return PlaceAPI(api_client, api_key=config.api_key)
```

This is like casting the actor before the scene starts.

The test never creates `PlaceAPI` manually. Pytest injects it.

## Scene 3: The API Layer Knows The Route

The API layer is:

```text
api/place_api.py
```

This file knows the Rahul Shetty Place API endpoints:

```python
ADD_PLACE_ENDPOINT = "/maps/api/place/add/json"
DELETE_PLACE_ENDPOINT = "/maps/api/place/delete/json"
```

It has two important methods:

```python
add_place(payload)
delete_place(payload)
```

The test does not say:

```text
POST /maps/api/place/add/json
POST /maps/api/place/delete/json
```

The API layer says that.

This keeps tests clean.

The test speaks business language:

```python
place_api.add_place(payload)
place_api.delete_place({"place_id": place_id})
```

That reads like a real action.

## Scene 4: Test Data Enters The Frame

The base body lives here:

```text
test_data/json/add_place_payload.json
```

It contains common request fields:

```text
location
accuracy
name
phone_number
address
types
website
language
```

The different test cases live here:

```text
test_data/json/add_place_test_cases.json
```

That file has multiple rows:

```json
[
  {
    "name": "Frontline house",
    "language": "French-IN",
    "accuracy": 50
  },
  {
    "name": "Automation villa",
    "language": "English-IN",
    "accuracy": 75
  },
  {
    "name": "API learning center",
    "language": "Hindi-IN",
    "accuracy": 100
  }
]
```

That is why this framework is data-driven.

The test code stays the same.

The data changes outside the code.

## Scene 5: Parameterization, The Montage

This line is where pytest creates a montage:

```python
@pytest.mark.parametrize(
    "place_data",
    ADD_PLACE_TEST_CASES,
    ids=lambda place_data: str(place_data["name"]),
)
```

It means:

```text
Run the same test once for each data row.
```

So one test function becomes three test executions:

```text
test_add_place_success[Frontline house]
test_add_place_success[Automation villa]
test_add_place_success[API learning center]
```

The `ids` part gives each test a readable name in terminal and report.

Without `ids`, the test names would be less friendly.

With `ids`, the report tells a clear story.

## Scene 6: The Payload Is Prepared

The helper function:

```python
def _add_place_payload(place_data: dict[str, Any]) -> dict[str, Any]:
```

builds the final request body.

It first reads the base payload:

```python
payload = deepcopy(read_json(ADD_PLACE_PAYLOAD_PATH))
```

Then it applies the current test data:

```python
payload.update(place_data)
```

So for `Automation villa`, the final payload becomes:

```json
{
  "name": "Automation villa",
  "language": "English-IN",
  "accuracy": 75
}
```

plus all the common fields from the base payload.

`deepcopy` is important because the payload contains nested data like
`location`. It prevents one test case from accidentally changing data for
another test case.

## Scene 7: The Add Place Request Is Sent

The test calls:

```python
response = place_api.add_place(payload)
```

This travels through the layers:

```text
test_places.py
  -> api/place_api.py
  -> core/api_client.py
  -> requests library
  -> Rahul Shetty API
```

The real request becomes:

```text
POST https://rahulshettyacademy.com/maps/api/place/add/json?key=qaclick123
```

The body is the JSON payload.

## Scene 8: The Response Is Judged

After the response comes back, the test validates it:

```python
response.should_have_status(200).should_match_schema(add_schema).should_have_value(
    "status", "OK"
)
```

This checks three things:

```text
HTTP status is 200
Response body matches schema
Response status field is OK
```

The schema lives here:

```text
schemas/add_place_success_schema.json
```

The schema says:

```text
status must exist
place_id must exist
scope must exist
reference must exist
id must exist
```

This is stronger than only checking status code.

Status code tells us:

```text
The API responded.
```

Schema tells us:

```text
The API responded in the expected format.
```

## Scene 9: The Identity Is Captured

The API creates a place and returns:

```json
{
  "status": "OK",
  "place_id": "abc123",
  "scope": "APP",
  "reference": "...",
  "id": "..."
}
```

The test captures the identity:

```python
place_id = response.json()["place_id"]
```

Then it stores it:

```python
CREATED_PLACE_IDS[str(place_data["name"])] = place_id
```

The dictionary becomes something like:

```python
{
    "Frontline house": "abc123",
    "Automation villa": "def456",
    "API learning center": "ghi789"
}
```

This is the bridge between add and delete.

## Scene 10: The Delete Test Returns

The delete test is separate:

```python
def test_delete_place_success(place_api: PlaceAPI, place_data: dict[str, Any]) -> None:
```

It is also parameterized with the same test data.

So it runs three times:

```text
test_delete_place_success[Frontline house]
test_delete_place_success[Automation villa]
test_delete_place_success[API learning center]
```

It gets the matching name:

```python
place_name = str(place_data["name"])
```

Then gets the matching `place_id`:

```python
place_id = CREATED_PLACE_IDS[place_name]
```

So:

```text
Frontline house deletes the place created by Frontline house
Automation villa deletes the place created by Automation villa
API learning center deletes the place created by API learning center
```

## Scene 11: The Delete Request Is Sent

The test calls:

```python
delete_response = place_api.delete_place({"place_id": place_id})
```

The real request becomes:

```text
POST https://rahulshettyacademy.com/maps/api/place/delete/json?key=qaclick123
```

The body is:

```json
{
  "place_id": "abc123"
}
```

## Scene 12: The Delete Response Is Verified

The delete response is checked:

```python
delete_response.should_have_status(200).should_match_schema(delete_schema).should_have_value(
    "status", "OK"
)
```

The delete schema lives here:

```text
schemas/delete_place_success_schema.json
```

It expects:

```json
{
  "status": "OK"
}
```

## Scene 13: The Core Engine

Behind the scenes, all API requests pass through:

```text
core/api_client.py
```

This is the engine.

It handles:

```text
base URL
query parameters
JSON body
timeout
SSL verification
retry setup
logging
Allure attachments
response wrapping
```

Because of `APIClient`, the test does not need to know low-level request logic.

The test stays readable.

## Scene 14: ResponseWrapper, The Translator

Raw HTTP responses are wrapped by:

```text
core/response_wrapper.py
```

That is why we can write:

```python
response.should_have_status(200)
response.should_match_schema(schema)
response.should_have_value("status", "OK")
```

This is easier to read than writing raw assertions everywhere.

## Scene 15: The Report

At the end, the framework creates reports:

```text
reports/report.html
reports/allure-report.html
```

The report contains:

```text
which tests ran
which tests passed
which tests failed
request details
response details
response body
response time
```

The report is the final scene.

It tells whether the mission succeeded.

## The Whole Film In One Flow

```text
pytest command starts
  -> qa.env loads base URL and API key
  -> fixtures create APIClient and PlaceAPI
  -> JSON test data is loaded
  -> pytest parameterizes add test into 3 cases
  -> Add Place API is called 3 times
  -> each place_id is stored
  -> pytest parameterizes delete test into 3 cases
  -> Delete Place API is called for each stored place_id
  -> response schemas validate API contracts
  -> reports are generated
```

## One Important Warning

This design intentionally connects the delete test to the add test:

```python
CREATED_PLACE_IDS
```

That means:

```text
add tests must run before delete tests
```

So avoid running this file in parallel:

```bash
.venv/bin/python -m pytest tests/test_places.py -n auto
```

For this learning framework, the design is useful because it clearly shows:

```text
how one API response feeds another API request
```

## Final Line

This framework is a small automation story:

```text
Data gives the scene.
Pytest runs the scene.
PlaceAPI performs the action.
APIClient carries the request.
Schema judges the response.
Reports tell the ending.
```

