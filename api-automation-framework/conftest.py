"""Pytest configuration, options, hooks, and fixture registration."""

from __future__ import annotations

import os
import json
import shutil
import subprocess
from dataclasses import replace
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pytest

from core.config import FrameworkConfig
from core.logger import get_logger

pytest_plugins: list[str] = [
    "fixtures.api_fixtures",
]


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register framework command-line options."""
    parser.addoption(
        "--env",
        action="store",
        default="qa",
        choices=("qa", "uat", "prod"),
        help="Target test environment.",
    )
    parser.addoption(
        "--no-open-allure-report",
        action="store_true",
        help="Do not open the Allure report automatically after test execution.",
    )
    parser.addoption(
        "--allure-html-report",
        action="store",
        default="reports/allure-report.html",
        help="Standalone HTML file generated from Allure results.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers and initialize report directories."""
    config.addinivalue_line("markers", "smoke: critical smoke tests")
    config.addinivalue_line("markers", "regression: broader regression tests")
    config.addinivalue_line("markers", "external: tests that call an external API service")
    Path("reports").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def config(pytestconfig: pytest.Config) -> FrameworkConfig:
    """Return the loaded framework configuration for the selected environment."""
    env = str(pytestconfig.getoption("--env"))
    loaded_config = FrameworkConfig.load(env)
    loaded_config = _with_worker_localhost_port(loaded_config)
    get_logger("pytest").info("Loaded %s environment: %s", env, loaded_config.base_url)
    return loaded_config


def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> None:
    """Attach basic call-phase logging for each test report."""
    if call.when == "call":
        get_logger("pytest").info("Executed test %s with outcome=%s", item.nodeid, call.excinfo)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Create and open a standalone HTML report from Allure results."""
    if _should_skip_allure_html_generation(session.config):
        return

    alluredir = _get_allure_results_dir(session.config)
    if alluredir is None or not alluredir.exists() or not any(alluredir.iterdir()):
        get_logger("pytest").warning("Allure HTML report was not created because no results were found.")
        return

    report_path = _get_allure_html_report_path(session.config)
    _write_allure_html_report(alluredir, report_path)
    get_logger("pytest").info("Generated standalone Allure HTML report at %s", report_path)

    if not _should_skip_auto_allure_open(session.config):
        _open_html_report(report_path)
        get_logger("pytest").info("Opening standalone Allure HTML report from %s", report_path)


def _with_worker_localhost_port(config: FrameworkConfig) -> FrameworkConfig:
    """Return config with a unique local port for each xdist worker."""
    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    if not worker_id or not worker_id.startswith("gw"):
        return config

    parsed_url = urlparse(config.base_url)
    if parsed_url.hostname not in {"127.0.0.1", "localhost"} or parsed_url.port is None:
        return config

    worker_index = int(worker_id.removeprefix("gw"))
    netloc = f"{parsed_url.hostname}:{parsed_url.port + worker_index}"
    worker_url = parsed_url._replace(netloc=netloc).geturl()
    return replace(config, base_url=worker_url)


def _should_skip_allure_html_generation(config: pytest.Config) -> bool:
    """Return whether the current run should avoid report generation."""
    return (
        bool(getattr(config, "workerinput", None))
        or bool(config.getoption("collectonly", default=False))
    )


def _should_skip_auto_allure_open(config: pytest.Config) -> bool:
    """Return whether the current run should avoid opening a local browser."""
    return (
        bool(config.getoption("--no-open-allure-report"))
        or bool(os.environ.get("CI"))
        or bool(os.environ.get("BUILD_NUMBER"))
    )


def _get_allure_results_dir(config: pytest.Config) -> Path | None:
    """Return the configured Allure results directory, if Allure is active."""
    alluredir = config.getoption("--alluredir", default=None)
    if alluredir is None:
        return None

    return Path(str(alluredir))


def _get_allure_html_report_path(config: pytest.Config) -> Path:
    """Return the configured standalone Allure HTML report path."""
    return Path(str(config.getoption("--allure-html-report")))


def _write_allure_html_report(alluredir: Path, report_path: Path) -> None:
    """Write a single-file HTML report using Allure result JSON files."""
    results = _read_allure_results(alluredir)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_allure_html(results, alluredir), encoding="utf-8")


def _read_allure_results(alluredir: Path) -> list[dict[str, Any]]:
    """Read Allure test result files sorted by test start time."""
    results: list[dict[str, Any]] = []
    for result_file in alluredir.glob("*-result.json"):
        try:
            result = json.loads(result_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            get_logger("pytest").warning("Skipping invalid Allure result file: %s", result_file)
            continue
        results.append(result)

    return sorted(results, key=lambda result: int(result.get("start") or 0))


def _render_allure_html(results: list[dict[str, Any]], alluredir: Path) -> str:
    """Render complete standalone HTML for Allure results."""
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_counts = _count_statuses(results)
    total_duration = sum(
        max(0, int(result.get("stop") or 0) - int(result.get("start") or 0))
        for result in results
    )

    rows = "\n".join(_render_result(result, alluredir) for result in results)
    summary_cards = "\n".join(
        f'<div class="card {status}"><span>{escape(status.title())}</span><strong>{count}</strong></div>'
        for status, count in status_counts.items()
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Allure HTML Report</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #1f2937; background: #f6f8fb; }}
    header {{ padding: 28px 36px; color: #fff; background: #243447; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    main {{ padding: 24px 36px 40px; }}
    .meta {{ color: #d6dee8; }}
    .summary {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 22px; }}
    .card {{ min-width: 130px; padding: 14px 16px; background: #fff; border-left: 5px solid #94a3b8; box-shadow: 0 1px 4px rgba(15, 23, 42, .08); }}
    .card span {{ display: block; font-size: 13px; color: #64748b; }}
    .card strong {{ display: block; margin-top: 6px; font-size: 26px; }}
    .passed {{ border-color: #16a34a; }}
    .failed, .broken {{ border-color: #dc2626; }}
    .skipped {{ border-color: #f59e0b; }}
    .unknown {{ border-color: #64748b; }}
    details {{ margin: 12px 0; background: #fff; border: 1px solid #e5e7eb; border-radius: 6px; }}
    summary {{ cursor: pointer; padding: 14px 16px; font-weight: 700; }}
    .result-body {{ padding: 0 16px 16px; }}
    .status {{ display: inline-block; min-width: 70px; margin-right: 10px; padding: 3px 8px; border-radius: 12px; color: #fff; text-align: center; font-size: 12px; }}
    .status.passed {{ background: #16a34a; }}
    .status.failed, .status.broken {{ background: #dc2626; }}
    .status.skipped {{ background: #f59e0b; }}
    .status.unknown {{ background: #64748b; }}
    dl {{ display: grid; grid-template-columns: 150px 1fr; gap: 8px 12px; }}
    dt {{ color: #64748b; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    pre {{ overflow: auto; padding: 12px; background: #111827; color: #f8fafc; border-radius: 6px; }}
    .empty {{ padding: 20px; background: #fff; border: 1px solid #e5e7eb; border-radius: 6px; }}
  </style>
</head>
<body>
  <header>
    <h1>Allure HTML Report</h1>
    <div class="meta">Generated {escape(generated_at)} | Tests: {len(results)} | Duration: {_format_duration(total_duration)}</div>
  </header>
  <main>
    <section class="summary">{summary_cards}</section>
    <section>
      {rows if rows else '<div class="empty">No Allure test results found.</div>'}
    </section>
  </main>
</body>
</html>
"""


def _render_result(result: dict[str, Any], alluredir: Path) -> str:
    """Render one Allure result into an expandable HTML block."""
    status = str(result.get("status") or "unknown")
    name = str(result.get("name") or "Unnamed test")
    duration = max(0, int(result.get("stop") or 0) - int(result.get("start") or 0))
    labels = result.get("labels") if isinstance(result.get("labels"), list) else []
    tags = ", ".join(
        str(label.get("value"))
        for label in labels
        if isinstance(label, dict) and label.get("name") == "tag"
    )
    attachments = "\n".join(_render_attachment(attachment, alluredir) for attachment in _as_list(result.get("attachments")))
    parameters = ", ".join(
        f"{parameter.get('name')}={parameter.get('value')}"
        for parameter in _as_list(result.get("parameters"))
        if isinstance(parameter, dict)
    )
    status_details = result.get("statusDetails") if isinstance(result.get("statusDetails"), dict) else {}
    failure_message = status_details.get("message") or status_details.get("trace") or ""

    return f"""<details>
  <summary><span class="status {escape(status)}">{escape(status)}</span>{escape(name)}</summary>
  <div class="result-body">
    <dl>
      <dt>Full name</dt><dd>{escape(str(result.get("fullName") or ""))}</dd>
      <dt>Description</dt><dd>{escape(str(result.get("description") or ""))}</dd>
      <dt>Duration</dt><dd>{_format_duration(duration)}</dd>
      <dt>Tags</dt><dd>{escape(tags)}</dd>
      <dt>Parameters</dt><dd>{escape(parameters)}</dd>
    </dl>
    {_render_pre("Failure", str(failure_message)) if failure_message else ""}
    {attachments}
  </div>
</details>"""


def _render_attachment(attachment: Any, alluredir: Path) -> str:
    """Render an Allure attachment inline."""
    if not isinstance(attachment, dict):
        return ""

    source = attachment.get("source")
    if not source:
        return ""

    attachment_path = alluredir / str(source)
    if not attachment_path.exists():
        return ""

    attachment_text = attachment_path.read_text(encoding="utf-8", errors="replace")
    title = str(attachment.get("name") or source)
    return _render_pre(title, attachment_text)


def _render_pre(title: str, value: str) -> str:
    """Render a titled preformatted text block."""
    return f"<h3>{escape(title)}</h3><pre>{escape(value)}</pre>"


def _count_statuses(results: list[dict[str, Any]]) -> dict[str, int]:
    """Return ordered Allure status counts."""
    counts = {"passed": 0, "failed": 0, "broken": 0, "skipped": 0, "unknown": 0}
    for result in results:
        status = str(result.get("status") or "unknown")
        counts[status if status in counts else "unknown"] += 1
    return counts


def _format_duration(milliseconds: int) -> str:
    """Format milliseconds as a compact duration."""
    seconds = milliseconds / 1000
    return f"{seconds:.2f}s"


def _as_list(value: Any) -> list[Any]:
    """Return value when it is a list, otherwise an empty list."""
    return value if isinstance(value, list) else []


def _open_html_report(report_path: Path) -> None:
    """Open an HTML file with the operating system default browser."""
    opener = shutil.which("open") or shutil.which("xdg-open")
    if opener is None:
        get_logger("pytest").warning("Could not open %s because no browser opener was found.", report_path)
        return

    subprocess.run([opener, report_path.resolve().as_uri()], check=False)
