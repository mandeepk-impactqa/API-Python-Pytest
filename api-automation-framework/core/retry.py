"""Retry policy creation for transient API failures."""

from __future__ import annotations

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

RETRY_STATUS_CODES = (500, 502, 503, 504)
RETRY_METHODS = frozenset({"HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST", "PATCH"})


def create_retry_adapter(total: int, backoff_factor: float) -> HTTPAdapter:
    """Create a requests HTTP adapter configured for transient retry handling."""
    retry_strategy = Retry(
        total=total,
        connect=total,
        read=total,
        status=total,
        allowed_methods=RETRY_METHODS,
        status_forcelist=RETRY_STATUS_CODES,
        backoff_factor=backoff_factor,
        raise_on_status=False,
    )
    return HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=50)
