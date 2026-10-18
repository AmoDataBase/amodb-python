"""Path and parameter building. Plain functions, no I/O.

Both clients call ``build`` and hand the ``(path, params)`` pair to their own
``request`` method, so the sync and async resources never repeat this logic.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

from ._core import DEFAULT_IMAGE_BASE_URL

Request = tuple[str, dict[str, Any]]


def segment(value: object) -> str:
    """Percent-encode one path segment. Empty or missing values are an error."""
    text = "" if value is None else str(value)
    if not text:
        raise ValueError("A required path value is missing")
    return quote(text, safe="")


def build(template: str, *segments: object, language: str | None = None, **params: Any) -> Request:
    """Return ``(path, params)`` for a template such as ``"/movie/{}/credits"``.

    Each ``{}`` in the template is filled with one encoded segment. Keyword values
    that are None are skipped. A ``params`` mapping is merged first, so named
    keywords win over it. ``language`` is added last when given.
    """
    query: dict[str, Any] = {}
    nested = params.pop("params", None)
    if nested:
        query.update(nested)
    for key, value in params.items():
        if value is not None:
            query[key] = value
    if language is not None:
        query["language"] = language
    return template.format(*(segment(s) for s in segments)), query


def image_url(
    path: str | None, size: str = "w500", base_url: str = DEFAULT_IMAGE_BASE_URL
) -> str | None:
    """Join an image base URL, a size and a file path. Returns None for an empty path."""
    if not path:
        return None
    if not path.startswith("/"):
        path = "/" + path
    base = base_url if base_url.endswith("/") else base_url + "/"
    return f"{base}{size}{path}"


def merge(*maps: Mapping[str, Any] | None) -> dict[str, Any]:
    """Merge parameter maps left to right, skipping None values."""
    out: dict[str, Any] = {}
    for item in maps:
        if item:
            out.update({k: v for k, v in item.items() if v is not None})
    return out
