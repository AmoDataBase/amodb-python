"""Sync client specifics: context manager, injected httpx client, default sleep."""

from __future__ import annotations

import time

import httpx

import amodb
from helpers import KEY, Recorder, ok, rate_limited


def test_context_manager_closes_an_owned_client() -> None:
    recorder = Recorder(ok({"id": 550}))
    with amodb.Client(KEY, transport=httpx.MockTransport(recorder)) as client:
        assert client.movies.details(550) == {"id": 550}
        http = client._http
        assert not http.is_closed
    assert http.is_closed


def test_close_can_be_called_directly() -> None:
    client = amodb.Client(KEY, transport=httpx.MockTransport(Recorder()))
    client.close()
    assert client._http.is_closed


def test_injected_http_client_is_used_and_left_open() -> None:
    recorder = Recorder(ok({"id": 5}))
    http = httpx.Client(transport=httpx.MockTransport(recorder), timeout=99)
    with amodb.Client(KEY, http_client=http) as client:
        assert client.movies.details(5) == {"id": 5}
    assert not http.is_closed
    assert recorder.last.extensions["timeout"]["read"] == 99
    assert recorder.last.headers["authorization"] == f"Bearer {KEY}"
    http.close()


def test_explicit_timeout_overrides_an_injected_client() -> None:
    recorder = Recorder(ok())
    with httpx.Client(transport=httpx.MockTransport(recorder), timeout=99) as http:
        amodb.Client(KEY, http_client=http, timeout=4).configuration()
    assert recorder.last.extensions["timeout"]["read"] == 4


def test_httpx_timeout_object_is_accepted() -> None:
    recorder = Recorder(ok())
    timeout = httpx.Timeout(10, connect=2)
    with amodb.Client(KEY, transport=httpx.MockTransport(recorder), timeout=timeout) as client:
        client.configuration()
    assert recorder.last.extensions["timeout"]["connect"] == 2
    assert recorder.last.extensions["timeout"]["read"] == 10


def test_default_sleep_is_time_sleep() -> None:
    recorder = Recorder(rate_limited("0"), ok({"id": 9}))
    with amodb.Client(KEY, transport=httpx.MockTransport(recorder)) as client:
        started = time.monotonic()
        assert client.movies.details(9) == {"id": 9}
    assert len(recorder.requests) == 2
    assert time.monotonic() - started < 1


def test_default_client_follows_redirects() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/omdb":
            return httpx.Response(301, headers={"Location": "https://api.amodb.dev/omdb/?i=tt1"})
        return httpx.Response(200, json={"Response": "True", "imdbID": "tt1"})

    with amodb.Client(
        KEY, omdb_url="https://api.amodb.dev/omdb", transport=httpx.MockTransport(handler)
    ) as client:
        assert client.omdb.by_id("tt1")["imdbID"] == "tt1"
