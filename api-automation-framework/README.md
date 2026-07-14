# API Testing Project

This project checks whether API services are working correctly.

An API is a way for one software system to talk to another software system. This
project sends requests to the API, checks the responses, and creates reports that
show what passed and what failed.

You do not need to understand the full code to run the tests.

## What This Project Does

- Runs API tests automatically.
- Checks the Rahul Shetty Academy Add Place API.
- Creates an HTML report after every run.
- Creates a single Allure HTML report file at `reports/allure-report.html`.
- Opens the Allure report automatically after execution.
- Uses Rahul Shetty Academy as the default API for real API practice.

## Main Folders

```text
api/          API actions such as adding a place
core/         Common code used by the framework
fixtures/     Test setup code
tests/        Actual test cases
test_data/    Input data used by tests
schemas/      Expected response formats
config/       Environment settings
reports/      Test reports
logs/         Execution logs
```

## First Time Setup

Open a terminal and go inside the project folder:

```bash
cd api-automation-framework
```

Create and activate a Python virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Run The Tests

Use this command:

```bash
.venv/bin/python -m pytest --env=qa
```

When the run finishes, the Allure report is created here:

```text
reports/allure-report.html
```

The report opens automatically in the browser.

## Run Without Opening The Report

Use this command when you only want to create the report file:

```bash
.venv/bin/python -m pytest --env=qa --no-open-allure-report
```

## Run Specific Test Groups

External API tests:

```bash
.venv/bin/python -m pytest --env=qa -m external
```

Regression tests:

```bash
.venv/bin/python -m pytest --env=qa -m regression
```

## Reports

After every test run, two HTML reports are available:

```text
reports/allure-report.html
reports/report.html
```

Use `reports/allure-report.html` as the main report. It is a single HTML file and
is easy to share.

## Environment

The default environment is `qa`.

Run QA:

```bash
.venv/bin/python -m pytest --env=qa
```

Run UAT:

```bash
.venv/bin/python -m pytest --env=uat
```

Run PROD:

```bash
.venv/bin/python -m pytest --env=prod
```

Environment files are stored here:

```text
config/qa.env
config/uat.env
config/prod.env
```

By default, `config/qa.env` points to the Rahul Shetty Academy API:

```text
https://rahulshettyacademy.com
```

For a real API, update `BASE_URL` in the correct environment file.

## Important Safety Note

Do not commit real passwords, tokens, or API keys into this project.

Use local environment files or CI/CD secrets for sensitive values.

## How The Tests Are Organized

Tests are stored inside the `tests/` folder.

Examples:

```text
tests/test_places.py
```

The test files do not call the API directly. They use reusable API files from the
`api/` folder. This keeps the tests cleaner and easier to maintain.

## Add A New API Test

For most new tests:

1. Add or update an API action inside the `api/` folder.
2. Add a test inside the `tests/` folder.
3. Add test data inside `test_data/` if needed.
4. Run the tests.
5. Check `reports/allure-report.html`.

## Test Data

Test data can be stored in different formats:

```text
JSON
```

Existing examples are available here:

```text
test_data/json/
```

## Useful Commands

Run all tests:

```bash
.venv/bin/python -m pytest --env=qa
```

Run tests and keep the report closed:

```bash
.venv/bin/python -m pytest --env=qa --no-open-allure-report
```

Create the Allure report at a different location:

```bash
.venv/bin/python -m pytest --env=qa --allure-html-report=reports/my-report.html
```

Run tests in parallel:

```bash
.venv/bin/python -m pytest --env=qa -n auto
```

## Docker

Build the Docker image:

```bash
docker build -t api-automation-framework .
```

Run the tests using Docker:

```bash
docker run --rm -v "$PWD/reports:/app/reports" -v "$PWD/logs:/app/logs" api-automation-framework
```

Run with Docker Compose:

```bash
TEST_ENV=qa docker compose up --build --abort-on-container-exit
```

## Simple Summary

Use this command most of the time:

```bash
.venv/bin/python -m pytest --env=qa
```

Then check this report:

```text
reports/allure-report.html
```
