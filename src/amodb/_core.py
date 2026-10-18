"""Logic shared by the sync and async clients.

Everything here is plain code with no I/O: settings, URL and header building,
query encoding, retry timing and response to result or error mapping.
"""

from __future__ import annotations

import json
import math
import time
from collections.abc import Coroutine, Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Literal, NamedTuple, Union
from urllib.parse import quote, urlsplit

import httpx

from ._version import __version__
from .errors import AmodbError, AmodbTimeoutError, NetworkError, RateLimitError

DEFAULT_BASE_URL = "https://api.amodb.dev/3"
DEFAULT_OMDB_URL = "https://api.amodb.dev/omdb/"
DEFAULT_IMAGE_BASE_URL = "https://img.amodb.dev/t/p/"
DEFAULT_TIMEOUT = 15.0
DEFAULT_MAX_RETRIES = 3
MAX_RETRIES_CAP = 3
MAX_RETRY_WAIT = 60
USER_AGENT = f"amodb-python/{__version__}"

AuthMode = Literal["bearer", "query"]
JSON = dict[str, Any]
AsyncJSON = Coroutine[Any, Any, JSON]
TimeoutValue = Union[float, httpx.Timeout]


@dataclass(frozen=True)
class Settings:
    """Validated client options. The API key is hidden from ``repr``."""

    api_key: str = field(repr=False)
    base_url: str
    omdb_url: str
    image_base_url: str
    language: str | None
    timeout: TimeoutValue
    max_retries: int
    auth: str


class PreparedRequest(NamedTuple):
    url: str
    headers: dict[str, str]


def make_settings(
    api_key: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    omdb_url: str = DEFAULT_OMDB_URL,
    image_base_url: str = DEFAULT_IMAGE_BASE_URL,
    language: str | None = None,
    timeout: TimeoutValue | None = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    auth: str = "bearer",
) -> Settings:
    """Validate options and apply defaults. Raises ValueError on bad input."""
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("api_key is required. Get a key at https://amodb.dev/pricing")
    if auth not in ("bearer", "query"):
        raise ValueError(f'auth must be "bearer" or "query", got {auth!r}')
    return Settings(
        api_key=api_key.strip(),
        base_url=base_url.rstrip("/"),
        omdb_url=omdb_url,
        image_base_url=image_base_url if image_base_url.endswith("/") else image_base_url + "/",
        language=language or None,
        timeout=DEFAULT_TIMEOUT if timeout is None else timeout,
        max_retries=clamp_retries(max_retries),
        auth=auth,
    )


def clamp_retries(value: int) -> int:
    """Keep ``max_retries`` between 0 and the hard cap of 3."""
    return max(0, min(int(value), MAX_RETRIES_CAP))


def timeout_for(timeout: TimeoutValue | None, injected_client: bool) -> Any:
    """Per request timeout. An injected client keeps its own unless one was given."""
    if timeout is not None:
        return timeout
    return httpx.USE_CLIENT_DEFAULT if injected_client else DEFAULT_TIMEOUT


# --- query encoding ---------------------------------------------------------


def format_value(value: Any) -> str | None:
    """Turn one parameter value into its wire text, or None to drop it."""
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, (list, tuple, set, frozenset)):
        items = sorted(value, key=str) if isinstance(value, (set, frozenset)) else value
        parts = [p for p in (format_value(item) for item in items) if p]
        return ",".join(parts) if parts else None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def encode_query(params: Mapping[str, Any]) -> str:
    """Build a query string. Keys are sent as given, values are percent-encoded."""
    pairs = []
    for key, value in params.items():
        text = format_value(value)
        if text is None:
            continue
        pairs.append(f"{quote(str(key), safe='')}={quote(text, safe=',')}")
    return "&".join(pairs)


def join_url(url: str, params: Mapping[str, Any]) -> str:
    query = encode_query(params)
    if not query:
        return url
    return f"{url}{'&' if '?' in url else '?'}{query}"


# --- request preparation ----------------------------------------------------


def _headers() -> dict[str, str]:
    return {"Accept": "application/json", "User-Agent": USER_AGENT}


def prepare_request(
    settings: Settings, path: str, params: Mapping[str, Any] | None = None
) -> PreparedRequest:
    """TMDB style call: default language, key as Bearer header or as ``api_key``."""
    merged: dict[str, Any] = dict(params) if params else {}
    merged.pop("api_key", None)
    if merged.get("language") is None and settings.language:
        merged["language"] = settings.language
    headers = _headers()
    if settings.auth == "query":
        merged["api_key"] = settings.api_key
    else:
        headers["Authorization"] = f"Bearer {settings.api_key}"
    if not path.startswith("/"):
        path = "/" + path
    return PreparedRequest(join_url(settings.base_url + path, merged), headers)


def prepare_omdb(settings: Settings, params: Mapping[str, Any]) -> PreparedRequest:
    """OMDb call: the key always travels as the ``apikey`` query parameter."""
    merged = {k: v for k, v in params.items() if k.lower() != "apikey"}
    merged["apikey"] = settings.api_key
    return PreparedRequest(join_url(settings.omdb_url, merged), _headers())


def plans_url(base_url: str) -> str:
    """The public plans URL, taken from the origin of the base URL."""
    parts = urlsplit(base_url)
    return f"{parts.scheme}://{parts.netloc}/plans"


def prepare_public(url: str) -> PreparedRequest:
    """A call that sends no key."""
    return PreparedRequest(url, _headers())


# --- retries ----------------------------------------------------------------


def parse_retry_after(value: str | None, now: float | None = None) -> int | None:
    """Read ``Retry-After`` as whole seconds. Accepts a number or an HTTP date."""
    if value is None or not value.strip():
        return None
    text = value.strip()
    try:
        seconds = float(text)
    except ValueError:
        try:
            when = parsedate_to_datetime(text)
        except (TypeError, ValueError, IndexError):
            return None
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        seconds = when.timestamp() - (time.time() if now is None else now)
    if not math.isfinite(seconds):
        return None
    return max(0, math.ceil(seconds))


def retry_delay(retry_after: int | None, attempt: int) -> float:
    """Seconds to wait before retry number ``attempt`` (0 based).

    Uses ``Retry-After`` clamped to 0..60 when present, else 1, 2, 4 seconds.
    """
    if retry_after is not None:
        return float(max(0, min(retry_after, MAX_RETRY_WAIT)))
    return float(min(2**attempt, MAX_RETRY_WAIT))


def retry_wait(response: httpx.Response, attempt: int, max_retries: int) -> float | None:
    """Seconds to sleep before the next try, or None when the response is final."""
    if response.status_code != 429 or attempt >= max_retries:
        return None
    return retry_delay(parse_retry_after(response.headers.get("retry-after")), attempt)


# --- responses and errors ---------------------------------------------------


def _parse_body(text: str) -> Any:
    if not text:
        return None
    try:
        return json.loads(text)
    except ValueError:
        return text


def _status_code_from(body: Any) -> int | None:
    if not isinstance(body, dict):
        return None
    raw = body.get("status_code")
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.strip().isdigit():
        return int(raw)
    return None


def _message_from(body: Any) -> str | None:
    if not isinstance(body, dict):
        return None
    for key in ("status_message", "Error", "error", "message"):
        value = body.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def error_from_response(response: httpx.Response) -> AmodbError:
    """Build the typed error for a non success response."""
    status = response.status_code
    body = _parse_body(response.text)
    code = _status_code_from(body)
    message = _message_from(body) or f"HTTP {status} {response.reason_phrase}".strip()
    if status == 429:
        retry_after = parse_retry_after(response.headers.get("retry-after"))
        return RateLimitError(message, status, code, body, retry_after)
    return AmodbError(message, status, code, body)


def interpret(response: httpx.Response, *, omdb: bool = False) -> Any:
    """Return the parsed JSON of a success response, or raise the typed error."""
    if not response.is_success:
        raise error_from_response(response)
    text = response.text
    try:
        data = json.loads(text)
    except ValueError:
        raise AmodbError(
            "Response body is not valid JSON", response.status_code, None, text or None
        ) from None
    if omdb and isinstance(data, dict) and str(data.get("Response")).lower() == "false":
        message = data.get("Error")
        raise AmodbError(
            message if isinstance(message, str) and message else "OMDb request failed",
            response.status_code,
            None,
            data,
        )
    return data


def transport_error(exc: httpx.RequestError) -> AmodbError:
    """Map an httpx transport failure to a typed error."""
    detail = str(exc) or exc.__class__.__name__
    if isinstance(exc, httpx.TimeoutException):
        return AmodbTimeoutError(f"Request timed out: {detail}")
    return NetworkError(f"Network error: {detail}")
