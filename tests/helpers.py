"""Test helpers: scripted responses and a runner that runs one scenario on both clients."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable
from typing import Any

import httpx

import amodb

KEY = "0123456789abcdef0123456789abcdef"

TMDB_ERRORS = {
    (401, 7): "Invalid API key: You must be granted a valid key.",
    (401, 10): "Suspended API key: Access to your account has been suspended, contact amodb.",
    (402, 36): "Your plan has expired. Renew at https://amodb.dev/pricing",
    (404, 34): "The resource you requested could not be found.",
    (405, 37): "This method is not offered by amodb.",
    (500, 11): "Internal error: Something went wrong, contact amodb.",
    (504, 24): "Your request to the backend server timed out. Try again.",
}


class Reply:
    """A scripted response. A fresh ``httpx.Response`` is built for every request."""

    def __init__(
        self,
        status: int = 200,
        json: Any = None,
        text: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self.json = json
        self.text = text
        self.headers = headers or {}

    def build(self) -> httpx.Response:
        if self.text is not None:
            return httpx.Response(self.status, content=self.text.encode(), headers=self.headers)
        if self.json is not None:
            return httpx.Response(self.status, json=self.json, headers=self.headers)
        return httpx.Response(self.status, headers=self.headers)


def ok(body: Any = None) -> Reply:
    return Reply(200, json={"id": 1} if body is None else body)


def tmdb_error(status: int, code: int, message: str, **headers: str) -> Reply:
    body = {"success": False, "status_code": code, "status_message": message}
    return Reply(status, json=body, headers=headers)


def rate_limited(retry_after: str | None = None) -> Reply:
    headers = {} if retry_after is None else {"Retry-After": retry_after}
    message = "Your request count (21) is over the allowed limit of (20)."
    return tmdb_error(429, 25, message, **headers)


class Recorder:
    """A transport handler that records requests and replays scripted replies.

    The last reply repeats when the script runs out. An exception instance in the
    script is raised instead of returned.
    """

    def __init__(self, *script: Reply | Exception) -> None:
        self.script = list(script) or [ok()]
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        item = self.script[min(len(self.requests) - 1, len(self.script) - 1)]
        if isinstance(item, Exception):
            raise item
        return item.build()

    @property
    def last(self) -> httpx.Request:
        return self.requests[-1]

    @property
    def target(self) -> str:
        """Path and query of the last request exactly as sent."""
        return self.last.url.raw_path.decode()


class Runner:
    """Runs ``fn(client)`` on a fresh sync or async client wired to a Recorder."""

    def __init__(self, flavor: str, recorder: Recorder, **options: Any) -> None:
        self.flavor = flavor
        self.recorder = recorder
        self.options = options
        self.sleeps: list[float] = []

    @property
    def requests(self) -> list[httpx.Request]:
        return self.recorder.requests

    @property
    def last(self) -> httpx.Request:
        return self.recorder.last

    @property
    def target(self) -> str:
        return self.recorder.target

    def run(self, fn: Callable[[Any], Any]) -> Any:
        options = dict(self.options)
        api_key = options.pop("api_key", KEY)
        transport = httpx.MockTransport(self.recorder)
        if self.flavor == "sync":
            with amodb.Client(
                api_key, transport=transport, sleep=self.sleeps.append, **options
            ) as client:
                return fn(client)

        async def asleep(seconds: float) -> None:
            self.sleeps.append(seconds)

        async def main() -> Any:
            async with amodb.AsyncClient(
                api_key, transport=transport, sleep=asleep, **options
            ) as client:
                out = fn(client)
                return await out if inspect.isawaitable(out) else out

        return asyncio.run(main())
