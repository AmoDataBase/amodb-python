"""Typed errors raised by the amodb client."""

from __future__ import annotations

from typing import Any

__all__ = [
    "AmodbError",
    "AmodbTimeoutError",
    "NetworkError",
    "RateLimitError",
]


class AmodbError(Exception):
    """Base class for every error raised by this package.

    Attributes:
        status: HTTP status code, or 0 when no response was received.
        status_code: The numeric ``status_code`` from the TMDB style error body, or None.
        status_message: The ``status_message`` (or OMDb ``Error``) text, or a generic message.
        body: The parsed JSON body, the raw text when the body is not JSON, or None when empty.
    """

    status: int
    status_code: int | None
    status_message: str
    body: Any

    def __init__(
        self,
        status_message: str,
        status: int = 0,
        status_code: int | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(status_message, status, status_code, body)
        self.status = status
        self.status_code = status_code
        self.status_message = status_message
        self.body = body

    def __str__(self) -> str:
        details = []
        if self.status:
            details.append(f"HTTP {self.status}")
        if self.status_code is not None:
            details.append(f"code {self.status_code}")
        suffix = f" ({', '.join(details)})" if details else ""
        return f"{self.status_message}{suffix}"


class RateLimitError(AmodbError):
    """HTTP 429. Raised after the allowed retries are used up.

    ``retry_after`` is the ``Retry-After`` value in whole seconds, or None when the
    header was missing or could not be read.
    """

    retry_after: int | None

    def __init__(
        self,
        status_message: str,
        status: int = 429,
        status_code: int | None = None,
        body: Any = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(status_message, status, status_code, body)
        self.retry_after = retry_after
        self.args = (status_message, status, status_code, body, retry_after)


class AmodbTimeoutError(AmodbError):
    """The request did not finish within the configured timeout. ``status`` is 0."""


class NetworkError(AmodbError):
    """The request failed before a response arrived (DNS, connection, TLS). ``status`` is 0."""
