"""Custom exceptions raised by the API automation framework."""

from __future__ import annotations


class FrameworkError(Exception):
    """Base exception for framework-specific failures."""


class ConfigurationError(FrameworkError):
    """Raised when required configuration is missing or invalid."""


class APIClientError(FrameworkError):
    """Raised when an HTTP request cannot be completed successfully."""


class AuthenticationError(FrameworkError):
    """Raised when authentication setup or token refresh fails."""


class ResponseValidationError(FrameworkError):
    """Raised when a response does not satisfy an expected contract."""
