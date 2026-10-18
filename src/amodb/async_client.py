"""Asynchronous client."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable, Mapping
from types import TracebackType
from typing import Any, Union

import httpx

from ._core import (
    DEFAULT_BASE_URL,
    DEFAULT_IMAGE_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_OMDB_URL,
    JSON,
    AsyncJSON,
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

__all__ = ["AsyncClient"]

SleepFunc = Callable[[float], Union[Awaitable[None], None]]


class AsyncClient(ClientApi[AsyncJSON]):
    """Asynchronous amodb client built on ``httpx.AsyncClient``.

    It takes the same options as ``Client``. Every method returns a coroutine, so use
    ``await``. ``sleep`` may be a coroutine function or a plain function.

    Use it as an async context manager to close the connection pool::

        async with AsyncClient("KEY") as client:
            await client.movies.details(550)
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
        http_client: httpx.AsyncClient | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        sleep: SleepFunc | None = None,
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
        self._http: httpx.AsyncClient = (
            http_client
            if http_client is not None
            else httpx.AsyncClient(
                transport=transport, timeout=self._settings.timeout, follow_redirects=True
            )
        )
        self._sleep: SleepFunc = sleep or asyncio.sleep
        self._init_api()

    def __repr__(self) -> str:
        return f"AsyncClient(base_url={self._settings.base_url!r}, auth={self._settings.auth!r})"

    async def aclose(self) -> None:
        """Close the connection pool. A client passed as ``http_client`` stays open."""
        if self._owns_http:
            await self._http.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def request(self, path: str, params: Mapping[str, Any] | None = None) -> JSON:
        return await self._execute(prepare_request(self._settings, path, params))

    async def _omdb(self, params: Mapping[str, Any]) -> JSON:
        return await self._execute(prepare_omdb(self._settings, params), omdb=True)

    async def _plans(self) -> JSON:
        return await self._execute(prepare_public(plans_url(self._settings.base_url)))

    async def _execute(self, prepared: PreparedRequest, *, omdb: bool = False) -> JSON:
        attempt = 0
        while True:
            try:
                response = await self._http.request(
                    "GET", prepared.url, headers=prepared.headers, timeout=self._timeout
                )
            except httpx.RequestError as exc:
                raise transport_error(exc) from exc
            wait = retry_wait(response, attempt, self._settings.max_retries)
            if wait is None:
                result: JSON = interpret(response, omdb=omdb)
                return result
            slept = self._sleep(wait)
            if inspect.isawaitable(slept):
                await slept
            attempt += 1
