"""Native async tests: event loop behavior that the shared runner does not cover."""

from __future__ import annotations

import asyncio
import inspect
import time
from typing import Any

import httpx
import pytest

import amodb
from helpers import KEY, Recorder, ok, rate_limited

pytestmark = pytest.mark.anyio


def make_client(*script: Any, **options: Any) -> tuple[amodb.AsyncClient, Recorder]:
    recorder = Recorder(*script)
    client = amodb.AsyncClient(KEY, transport=httpx.MockTransport(recorder), **options)
    return client, recorder


async def test_async_context_manager_and_await() -> None:
    client, recorder = make_client(ok({"id": 550}))
    async with client:
        assert await client.movies.details(550) == {"id": 550}
    assert client._http.is_closed
    assert recorder.target == "/3/movie/550"


async def test_methods_return_real_coroutines() -> None:
    client, _ = make_client()
    async with client:
        call = client.movies.details(550)
        assert inspect.iscoroutine(call)
        assert await call == {"id": 1}
        task = asyncio.create_task(client.search.movie("x"))
        assert await task == {"id": 1}


async def test_gather_runs_calls_concurrently() -> None:
    client, recorder = make_client()
    async with client:
        results = await asyncio.gather(
            client.movies.details(1), client.tv.details(2), client.people.details(3)
        )
    assert list(results) == [{"id": 1}] * 3
    assert sorted(r.url.path for r in recorder.requests) == [
        "/3/movie/1",
        "/3/person/3",
        "/3/tv/2",
    ]


async def test_default_sleep_is_asyncio_sleep() -> None:
    client, recorder = make_client(rate_limited("0"), ok({"id": 9}))
    async with client:
        started = time.monotonic()
        assert await client.movies.details(9) == {"id": 9}
    assert len(recorder.requests) == 2
    assert time.monotonic() - started < 1


async def test_sync_sleep_function_is_accepted() -> None:
    sleeps: list[float] = []
    client, _ = make_client(rate_limited("2"), ok(), sleep=sleeps.append)
    async with client:
        await client.movies.details(1)
    assert sleeps == [2]


async def test_coroutine_sleep_function_is_awaited() -> None:
    sleeps: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        await asyncio.sleep(0)
        sleeps.append(seconds)

    client, _ = make_client(rate_limited("4"), ok(), sleep=fake_sleep)
    async with client:
        await client.movies.details(1)
    assert sleeps == [4]


async def test_injected_http_client_is_used_and_left_open() -> None:
    recorder = Recorder(ok({"id": 5}))
    http = httpx.AsyncClient(transport=httpx.MockTransport(recorder), timeout=99)
    async with amodb.AsyncClient(KEY, http_client=http) as client:
        assert await client.movies.details(5) == {"id": 5}
    assert not http.is_closed
    assert recorder.last.extensions["timeout"]["read"] == 99
    await http.aclose()


async def test_explicit_timeout_overrides_an_injected_client() -> None:
    recorder = Recorder(ok())
    http = httpx.AsyncClient(transport=httpx.MockTransport(recorder), timeout=99)
    async with http:
        client = amodb.AsyncClient(KEY, http_client=http, timeout=4)
        await client.configuration()
    assert recorder.last.extensions["timeout"]["read"] == 4


async def test_async_errors_are_typed() -> None:
    client, _ = make_client(httpx.ReadTimeout("slow"))
    async with client:
        with pytest.raises(amodb.AmodbTimeoutError):
            await client.movies.details(1)


async def test_async_image_helper_is_synchronous() -> None:
    client, _ = make_client()
    async with client:
        assert client.image_url("/a.jpg") == "https://img.amodb.dev/t/p/w500/a.jpg"
