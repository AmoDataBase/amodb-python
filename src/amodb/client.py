"""Synchronous client."""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from types import TracebackType
from typing import Any

import httpx

from ._core import (
    DEFAULT_BASE_URL,
    DEFAULT_IMAGE_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_OMDB_URL,
    JSON,
    AuthMode,
    PreparedRequest,
    TimeoutValue,
    interpret,
    make_settings,
    plans_url,
    prepare_omdb,
    prepare_public,
    prepare_request,
    retry_wait,
    timeout_for,
    transport_error,
)
from ._resources import ClientApi

__all__ = ["Client"]


class Client(ClientApi[JSON]):
    """Synchronous amodb client built on ``httpx.Client``.

    Args:
        api_key: Your amodb key. Required.
        base_url: TMDB style base URL. Default ``https://api.amodb.dev/3``.
        omdb_url: OMDb style URL. Default ``https://api.amodb.dev/omdb/``.
        image_base_url: Image base URL. Default ``https://img.amodb.dev/t/p/``.
        language: Default ``language`` sent with every TMDB style call. A per call value wins.
        timeout: Seconds, or an ``httpx.Timeout``. Default 15. With ``http_client`` the
            timeout of that client applies unless you pass one here.
        max_retries: Retries on HTTP 429. Default 3, never more than 3.
        auth: ``"bearer"`` sends ``Authorization: Bearer KEY``. ``"query"`` sends ``api_key=KEY``.
        http_client: Your own ``httpx.Client``. It is not closed by this client.
        transport: A custom ``httpx.BaseTransport``, for example ``httpx.MockTransport``.
        sleep: Replaces ``time.sleep`` for retry waits. Useful in tests.

    Use it as a context manager to close the connection pool::

        with Client("KEY") as client:
            client.movies.details(550)
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        omdb_url: str = DEFAULT_OMDB_URL,
        image_base_url: str = DEFAULT_IMAGE_BASE_URL,
        language: str | None = None,
        timeout: TimeoutValue | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        auth: AuthMode = "bearer",
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] | None = None,
    ) -> None:
        if http_client is not None and transport is not None:
            raise ValueError("Pass either http_client or transport, not both")
        self._settings = make_settings(
            api_key,
            base_url=base_url,
            omdb_url=omdb_url,
            image_base_url=image_base_url,
            language=language,
            timeout=timeout,
            max_retries=max_retries,
            auth=auth,
        )
        self._owns_http = http_client is None
        self._timeout: Any = timeout_for(timeout, http_client is not None)
        self._http: httpx.Client = (
            http_client
            if http_client is not None
            else httpx.Client(
                transport=transport, timeout=self._settings.timeout, follow_redirects=True
            )
        )
        self._sleep: Callable[[float], None] = sleep or time.sleep
        self._init_api()

    def __repr__(self) -> str:
        return f"Client(base_url={self._settings.base_url!r}, auth={self._settings.auth!r})"

    def close(self) -> None:
        """Close the connection pool. A client passed as ``http_client`` stays open."""
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def request(self, path: str, params: Mapping[str, Any] | None = None) -> JSON:
        return self._execute(prepare_request(self._settings, path, params))

    def _omdb(self, params: Mapping[str, Any]) -> JSON:
        return self._execute(prepare_omdb(self._settings, params), omdb=True)

    def _plans(self) -> JSON:
        return self._execute(prepare_public(plans_url(self._settings.base_url)))

    def _execute(self, prepared: PreparedRequest, *, omdb: bool = False) -> JSON:
        attempt = 0
        while True:
            try:
                response = self._http.request(
                    "GET", prepared.url, headers=prepared.headers, timeout=self._timeout
                )
            except httpx.RequestError as exc:
                raise transport_error(exc) from exc
            wait = retry_wait(response, attempt, self._settings.max_retries)
            if wait is None:
                result: JSON = interpret(response, omdb=omdb)
                return result
            self._sleep(wait)
            attempt += 1
