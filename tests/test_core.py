"""Unit tests for the shared helpers."""

from __future__ import annotations

import importlib.metadata
from datetime import date, datetime
from pathlib import Path

import pytest

import amodb
from amodb._core import (
    encode_query,
    format_value,
    make_settings,
    parse_retry_after,
    plans_url,
    retry_delay,
)
from amodb._endpoints import build, image_url, segment


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        (True, "true"),
        (False, "false"),
        (0, "0"),
        (7.5, "7.5"),
        ("a b", "a b"),
        ("", ""),
        ([1, 2, 3], "1,2,3"),
        (("credits", "images"), "credits,images"),
        ([], None),
        ([None, ""], None),
        ([True, "x"], "true,x"),
        ({"b", "a"}, "a,b"),
        (date(2020, 1, 2), "2020-01-02"),
        (datetime(2020, 1, 2, 3, 4, 5), "2020-01-02T03:04:05"),
        (b"bytes", "bytes"),
    ],
)
def test_format_value(value: object, expected: str | None) -> None:
    assert format_value(value) == expected


def test_encode_query_keeps_order_drops_none_and_encodes() -> None:
    params = {"b": 1, "a": None, "c d": "é&=", "e": [1, 2]}
    assert encode_query(params) == "b=1&c%20d=%C3%A9%26%3D&e=1,2"
    assert encode_query({}) == ""
    assert encode_query({"a": None}) == ""


def test_parse_retry_after() -> None:
    assert parse_retry_after(None) is None
    assert parse_retry_after("") is None
    assert parse_retry_after("  ") is None
    assert parse_retry_after("7") == 7
    assert parse_retry_after(" 7 ") == 7
    assert parse_retry_after("1.2") == 2
    assert parse_retry_after("-3") == 0
    assert parse_retry_after("nan") is None
    assert parse_retry_after("inf") is None
    assert parse_retry_after("tomorrow") is None
    # 2026-10-21 07:28:30 GMT is 1792567710 seconds after the epoch.
    assert parse_retry_after("Wed, 21 Oct 2026 07:28:30 GMT", now=1792567680.0) == 30
    assert parse_retry_after("Wed, 21 Oct 2026 07:28:00 GMT", now=1792567700.0) == 0


def test_retry_delay() -> None:
    assert [retry_delay(None, n) for n in range(3)] == [1, 2, 4]
    assert retry_delay(5, 0) == 5
    assert retry_delay(0, 2) == 0
    assert retry_delay(999, 0) == 60
    assert retry_delay(-4, 0) == 0
    assert retry_delay(None, 20) == 60


def test_make_settings_defaults() -> None:
    s = make_settings("secret-key")
    assert s.base_url == "https://api.amodb.dev/3"
    assert s.omdb_url == "https://api.amodb.dev/omdb/"
    assert s.image_base_url == "https://img.amodb.dev/t/p/"
    assert s.timeout == 15
    assert s.max_retries == 3
    assert s.auth == "bearer"
    assert s.language is None
    assert "secret-key" not in repr(s)


def test_make_settings_normalizes() -> None:
    s = make_settings(
        "k",
        base_url="https://x.test/3///",
        image_base_url="https://i.test/p",
        language="",
        max_retries=99,
    )
    assert s.base_url == "https://x.test/3"
    assert s.image_base_url == "https://i.test/p/"
    assert s.language is None
    assert s.max_retries == 3


def test_plans_url() -> None:
    assert plans_url("https://api.amodb.dev/3") == "https://api.amodb.dev/plans"
    assert plans_url("http://localhost:8787/3") == "http://localhost:8787/plans"


def test_build_merges_params_and_skips_none() -> None:
    path, query = build(
        "/movie/{}/x/{}", 5, "a b", page=None, language="ru-RU", params={"z": 1, "page": 9}, q="v"
    )
    assert path == "/movie/5/x/a%20b"
    assert query == {"z": 1, "page": 9, "q": "v", "language": "ru-RU"}


def test_build_named_values_win_over_the_params_map() -> None:
    _, query = build("/x", params={"page": 1}, page=2)
    assert query == {"page": 2}


def test_segment() -> None:
    assert segment(550) == "550"
    assert segment("tt0137523") == "tt0137523"
    assert segment("a/b") == "a%2Fb"
    for bad in (None, ""):
        with pytest.raises(ValueError, match="path value"):
            segment(bad)


def test_image_url_helper() -> None:
    assert image_url("/a.jpg", "w92") == "https://img.amodb.dev/t/p/w92/a.jpg"
    assert image_url(None) is None


def test_version_matches_installed_metadata() -> None:
    try:
        installed = importlib.metadata.version("amodb")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("package is not installed")
    assert installed == amodb.__version__ == "0.1.0"


def test_py_typed_marker_ships_with_the_package() -> None:
    assert (Path(amodb.__file__).parent / "py.typed").is_file()


def test_public_names() -> None:
    for name in amodb.__all__:
        assert hasattr(amodb, name)
    assert issubclass(amodb.RateLimitError, amodb.AmodbError)
    assert issubclass(amodb.AmodbTimeoutError, amodb.AmodbError)
    assert issubclass(amodb.NetworkError, amodb.AmodbError)
    assert issubclass(amodb.AmodbError, Exception)
