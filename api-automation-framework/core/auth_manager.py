"""Authentication strategies and token lifecycle management."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import jwt
import requests
from requests.auth import HTTPBasicAuth

from core.config import FrameworkConfig
from core.exceptions import AuthenticationError


@dataclass(slots=True)
class TokenState:
    """Current token and expiry metadata."""

    token: str | None = None
    expires_at: float = 0.0

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """Return whether the token is missing or close to expiry."""
        return not self.token or time.time() >= self.expires_at - buffer_seconds


class AuthManager:
    """Create auth headers and refresh supported token types."""

    def __init__(self, config: FrameworkConfig) -> None:
        """Initialize auth manager from runtime configuration."""
        self._config = config
        self._token_state = TokenState(
            token=config.bearer_token, expires_at=self._jwt_expiry(config.bearer_token)
        )

    def basic_auth(self) -> HTTPBasicAuth:
        """Return requests-compatible HTTP Basic authentication."""
        if not self._config.username or not self._config.password:
            raise AuthenticationError(
                "USERNAME and PASSWORD are required for basic authentication."
            )
        return HTTPBasicAuth(self._config.username, self._config.password)

    def bearer_headers(self) -> dict[str, str]:
        """Return Authorization header for bearer token authentication."""
        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

    def api_key_headers(self, header_name: str = "x-api-key") -> dict[str, str]:
        """Return API key headers using a configurable header name."""
        if not self._config.api_key:
            raise AuthenticationError("API_KEY is required for API key authentication.")
        return {header_name: self._config.api_key}

    def jwt_headers(self) -> dict[str, str]:
        """Return Authorization header for JWT authentication."""
        return self.bearer_headers()

    def get_access_token(self) -> str:
        """Return an access token, refreshing it automatically when needed."""
        if self._token_state.is_expired():
            self.refresh_oauth2_token()
        if not self._token_state.token:
            raise AuthenticationError("No bearer token is available.")
        return self._token_state.token

    def refresh_oauth2_token(self) -> None:
        """Refresh OAuth2 client-credentials token using configured token endpoint."""
        token_url = self._config.oauth_token_url
        client_id = self._config.client_id
        client_secret = self._config.client_secret

        if not all([token_url, client_id, client_secret]):
            if self._config.bearer_token:
                self._token_state = TokenState(
                    token=self._config.bearer_token,
                    expires_at=self._jwt_expiry(self._config.bearer_token),
                )
                return
            raise AuthenticationError(
                "OAuth2 token refresh requires token URL, client ID, and client secret."
            )

        if token_url is None or client_id is None or client_secret is None:
            raise AuthenticationError("OAuth2 token refresh configuration is incomplete.")

        response = requests.post(
            token_url,
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=self._config.timeout_seconds,
        )
        if response.status_code >= 400:
            raise AuthenticationError(
                f"OAuth2 token refresh failed with status {response.status_code}."
            )

        payload: dict[str, Any] = response.json()
        token = payload.get("access_token")
        if not token:
            raise AuthenticationError("OAuth2 token response did not include access_token.")
        expires_in = int(payload.get("expires_in", 3600))
        self._token_state = TokenState(token=token, expires_at=time.time() + expires_in)

    @staticmethod
    def _jwt_expiry(token: str | None) -> float:
        """Return JWT expiry timestamp without verifying the signature."""
        if not token:
            return 0.0
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            return float(decoded.get("exp", time.time() + 3600))
        except jwt.PyJWTError:
            return time.time() + 3600
