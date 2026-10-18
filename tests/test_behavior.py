"""Auth, language, retries, errors, OMDb, images and options. Runs on both clients."""

from __future__ import annotations

import time
from collections.abc import Callable
from email.utils import formatdate
from typing import Any

import httpx
import pytest

import amodb
from amodb import AmodbError, AmodbTimeoutError, NetworkError, RateLimitError
from helpers import KEY, TMDB_ERRORS, Reply, Runner, ok, rate_limited, tmdb_error

Make = Callable[..., Runner]


# --- auth -------------------------------------------------------------------


def test_bearer_header_is_the_default(make: Make) -> None:
    h = make()
    h.run(lambda c: c.movies.details(550))
    assert h.last.headers["authorization"] == f"Bearer {KEY}"
    assert KEY not in str(h.last.url)
    assert "api_key" not in h.last.url.params


def test_query_auth_mode(make: Make) -> None:
    h = make(auth="query")
    h.run(lambda c: c.movies.details(550, append_to_response=["credits"]))
    assert h.target == f"/3/movie/550?append_to_response=credits&api_key={KEY}"
    assert "authorization" not in h.last.headers


def test_query_auth_mode_on_bare_request(make: Make) -> None:
    h = make(auth="query")
    h.run(lambda c: c.configuration())
    assert h.target == f"/3/configuration?api_key={KEY}"


def test_key_param_in_user_params_never_leaks_in_bearer_mode(make: Make) -> None:
    h = make()
    h.run(lambda c: c.request("/configuration", {"api_key": "other"}))
    assert h.target == "/3/configuration"


def test_api_key_is_trimmed(make: Make) -> None:
    h = make(api_key=f"  {KEY}\n")
    h.run(lambda c: c.configuration())
    assert h.last.headers["authorization"] == f"Bearer {KEY}"


def test_user_agent_and_accept(make: Make) -> None:
    h = make()
    h.run(lambda c: c.configuration())
    assert h.last.headers["user-agent"] == f"amodb-python/{amodb.__version__}"
    assert h.last.headers["accept"] == "application/json"


@pytest.mark.parametrize("bad", ["", "   ", None])
def test_empty_key_fails_fast(bad: Any) -> None:
    with pytest.raises(ValueError, match="api_key is required"):
        amodb.Client(bad)
    with pytest.raises(ValueError, match="api_key is required"):
        amodb.AsyncClient(bad)


def test_bad_auth_mode_and_conflicting_options() -> None:
    with pytest.raises(ValueError, match="auth"):
        amodb.Client(KEY, auth="cookie")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="auth"):
        amodb.AsyncClient(KEY, auth="cookie")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="not both"):
        amodb.Client(KEY, http_client=httpx.Client(), transport=httpx.MockTransport(lambda r: r))
    with pytest.raises(ValueError, match="not both"):
        amodb.AsyncClient(
            KEY, http_client=httpx.AsyncClient(), transport=httpx.MockTransport(lambda r: r)
        )


def test_repr_hides_the_key() -> None:
    assert KEY not in repr(amodb.Client(KEY))
    assert KEY not in repr(amodb.AsyncClient(KEY))


# --- language ---------------------------------------------------------------


def test_no_language_by_default(make: Make) -> None:
    h = make()
    h.run(lambda c: c.movies.details(550))
    assert "language" not in h.last.url.params


def test_default_language_is_sent(make: Make) -> None:
    h = make(language="ru-RU")
    h.run(lambda c: c.movies.details(550))
    assert h.target == "/3/movie/550?language=ru-RU"


def test_per_call_language_overrides_default(make: Make) -> None:
    h = make(language="ru-RU")
    h.run(lambda c: c.movies.details(550, language="pt-BR"))
    assert h.target == "/3/movie/550?language=pt-BR"


def test_per_call_language_on_request_overrides_default(make: Make) -> None:
    h = make(language="ru-RU")
    h.run(lambda c: c.request("/movie/550", {"language": "fr-FR"}))
    assert h.target == "/3/movie/550?language=fr-FR"


def test_none_language_falls_back_to_default(make: Make) -> None:
    h = make(language="ru-RU")
    h.run(lambda c: c.request("/movie/550", {"language": None}))
    assert h.target == "/3/movie/550?language=ru-RU"


def test_default_language_is_not_sent_to_omdb_or_plans(make: Make) -> None:
    h = make(ok({"Response": "True"}), language="ru-RU")
    h.run(lambda c: c.omdb.by_id("tt0137523"))
    assert "language" not in h.last.url.params
    h2 = make(language="ru-RU")
    h2.run(lambda c: c.plans())
    assert h2.last.url.query == b""


# --- query and path encoding --------------------------------------------------


def test_append_to_response_is_joined_with_commas(make: Make) -> None:
    h = make()
    h.run(lambda c: c.movies.details(550, append_to_response=["credits", "images", "ratings"]))
    assert h.last.url.params["append_to_response"] == "credits,images,ratings"


def test_booleans_none_and_empty_lists(make: Make) -> None:
    h = make()
    h.run(lambda c: c.request("/x", {"a": True, "b": False, "c": None, "d": [], "e": [1, None, 2]}))
    assert h.target == "/3/x?a=true&b=false&e=1,2"


def test_keys_are_sent_as_given_and_values_are_encoded(make: Make) -> None:
    h = make()
    h.run(lambda c: c.request("/x", {"Some_Key.gte": "a b+c&d=e#f"}))
    assert h.target == "/3/x?Some_Key.gte=a%20b%2Bc%26d%3De%23f"


def test_path_segments_are_percent_encoded(make: Make) -> None:
    h = make()
    h.run(lambda c: c.find("a/b c?d", "imdb_id"))
    assert h.target == "/3/find/a%2Fb%20c%3Fd?external_source=imdb_id"


def test_missing_path_value_is_rejected(make: Make) -> None:
    h = make()
    with pytest.raises(ValueError, match="path value"):
        h.run(lambda c: c.movies.details(""))
    with pytest.raises(ValueError, match="path value"):
        h.run(lambda c: c.tv.season(1399, None))
    assert h.requests == []


def test_base_url_trailing_slash_and_path_without_slash(make: Make) -> None:
    h = make(base_url="https://example.test/3/")
    h.run(lambda c: c.request("movie/550"))
    assert str(h.last.url) == "https://example.test/3/movie/550"


def test_request_path_with_query_string(make: Make) -> None:
    h = make(language="ru-RU")
    h.run(lambda c: c.request("/discover/movie?with_genres=28", {"page": 2}))
    assert h.target == "/3/discover/movie?with_genres=28&page=2&language=ru-RU"


# --- retries ------------------------------------------------------------------


def test_429_retries_with_retry_after_then_gives_up(make: Make) -> None:
    h = make(rate_limited("2"))
    with pytest.raises(RateLimitError) as info:
        h.run(lambda c: c.movies.details(550))
    assert len(h.requests) == 4
    assert h.sleeps == [2, 2, 2]
    err = info.value
    assert err.status == 429
    assert err.status_code == 25
    assert err.retry_after == 2
    assert isinstance(err, AmodbError)


def test_429_then_success(make: Make) -> None:
    h = make(rate_limited("3"), ok({"id": 550}))
    assert h.run(lambda c: c.movies.details(550)) == {"id": 550}
    assert len(h.requests) == 2
    assert h.sleeps == [3]


def test_429_without_retry_after_backs_off_1_2_4(make: Make) -> None:
    h = make(rate_limited())
    with pytest.raises(RateLimitError) as info:
        h.run(lambda c: c.movies.details(550))
    assert h.sleeps == [1, 2, 4]
    assert info.value.retry_after is None


@pytest.mark.parametrize(
    ("header", "expected"),
    [("0", [0, 0, 0]), ("120", [60, 60, 60]), ("-5", [0, 0, 0]), ("soon", [1, 2, 4])],
)
def test_retry_after_is_clamped_or_ignored(make: Make, header: str, expected: list[float]) -> None:
    h = make(rate_limited(header))
    with pytest.raises(RateLimitError):
        h.run(lambda c: c.movies.details(550))
    assert h.sleeps == expected


def test_retry_after_http_date(make: Make) -> None:
    h = make(rate_limited(formatdate(time.time() + 30, usegmt=True)), ok())
    h.run(lambda c: c.movies.details(550))
    assert 27 <= h.sleeps[0] <= 31


def test_retry_after_http_date_in_the_past_means_no_wait(make: Make) -> None:
    h = make(rate_limited(formatdate(time.time() - 3600, usegmt=True)), ok())
    h.run(lambda c: c.movies.details(550))
    assert h.sleeps == [0]


def test_retry_after_error_value_is_not_clamped(make: Make) -> None:
    h = make(rate_limited("120"), max_retries=0)
    with pytest.raises(RateLimitError) as info:
        h.run(lambda c: c.movies.details(550))
    assert info.value.retry_after == 120


@pytest.mark.parametrize(
    ("max_retries", "attempts"), [(0, 1), (1, 2), (2, 3), (3, 4), (10, 4), (-1, 1)]
)
def test_max_retries_is_capped_at_3(make: Make, max_retries: int, attempts: int) -> None:
    h = make(rate_limited("1"), max_retries=max_retries)
    with pytest.raises(RateLimitError):
        h.run(lambda c: c.movies.details(550))
    assert len(h.requests) == attempts


@pytest.mark.parametrize("status", [400, 401, 404, 500, 502, 503, 504])
def test_only_429_is_retried(make: Make, status: int) -> None:
    h = make(Reply(status, json={"status_code": 1, "status_message": "x"}))
    with pytest.raises(AmodbError):
        h.run(lambda c: c.movies.details(550))
    assert len(h.requests) == 1
    assert h.sleeps == []


def test_omdb_and_plans_calls_retry_too(make: Make) -> None:
    h = make(rate_limited("1"), ok({"Response": "True"}))
    h.run(lambda c: c.omdb.by_id("tt0137523"))
    assert h.sleeps == [1]
    h2 = make(rate_limited("1"), ok({"plans": []}))
    h2.run(lambda c: c.plans())
    assert h2.sleeps == [1]


# --- errors -------------------------------------------------------------------


@pytest.mark.parametrize(("key", "message"), list(TMDB_ERRORS.items()), ids=str)
def test_tmdb_error_body_maps_to_typed_error(
    make: Make, key: tuple[int, int], message: str
) -> None:
    status, code = key
    body = {"success": False, "status_code": code, "status_message": message}
    h = make(tmdb_error(status, code, message))
    with pytest.raises(AmodbError) as info:
        h.run(lambda c: c.movies.details(550))
    err = info.value
    assert type(err) is AmodbError
    assert err.status == status
    assert err.status_code == code
    assert err.status_message == message
    assert err.body == body
    assert message in str(err)
    assert f"HTTP {status}" in str(err)


def test_rate_limit_error_carries_the_tmdb_fields(make: Make) -> None:
    h = make(rate_limited("5"), max_retries=0)
    with pytest.raises(RateLimitError) as info:
        h.run(lambda c: c.movies.details(550))
    err = info.value
    assert err.status_message == "Your request count (21) is over the allowed limit of (20)."
    assert err.body["status_code"] == 25
    assert err.retry_after == 5


def test_non_json_error_body(make: Make) -> None:
    h = make(Reply(503, text="<html>Service Unavailable</html>"))
    with pytest.raises(AmodbError) as info:
        h.run(lambda c: c.movies.details(550))
    err = info.value
    assert type(err) is AmodbError
    assert err.status == 503
    assert err.status_code is None
    assert err.body == "<html>Service Unavailable</html>"
    assert err.status_message == "HTTP 503 Service Unavailable"


def test_empty_error_body(make: Make) -> None:
    h = make(Reply(500))
    with pytest.raises(AmodbError) as info:
        h.run(lambda c: c.movies.details(550))
    err = info.value
    assert err.status == 500
    assert err.status_code is None
    assert err.body is None
    assert err.status_message == "HTTP 500 Internal Server Error"


def test_json_error_body_without_tmdb_fields(make: Make) -> None:
    h = make(Reply(418, json={"oops": True}))
    with pytest.raises(AmodbError) as info:
        h.run(lambda c: c.movies.details(550))
    assert info.value.status == 418
    assert info.value.status_code is None
    assert info.value.body == {"oops": True}


def test_success_with_a_non_json_body_is_an_error(make: Make) -> None:
    h = make(Reply(200, text="not json"))
    with pytest.raises(AmodbError) as info:
        h.run(lambda c: c.movies.details(550))
    assert info.value.status == 200
    assert info.value.body == "not json"


def test_timeout_maps_to_timeout_error(make: Make) -> None:
    h = make(httpx.ReadTimeout("took too long"))
    with pytest.raises(AmodbTimeoutError) as info:
        h.run(lambda c: c.movies.details(550))
    err = info.value
    assert isinstance(err, AmodbError)
    assert err.status == 0
    assert err.status_code is None
    assert isinstance(err.__cause__, httpx.ReadTimeout)
    assert len(h.requests) == 1


def test_connection_failure_maps_to_network_error(make: Make) -> None:
    h = make(httpx.ConnectError("refused"))
    with pytest.raises(NetworkError) as info:
        h.run(lambda c: c.movies.details(550))
    assert info.value.status == 0
    assert "refused" in info.value.status_message
    assert not isinstance(info.value, AmodbTimeoutError)


def test_timeout_option_reaches_the_request(make: Make) -> None:
    h = make()
    h.run(lambda c: c.configuration())
    assert h.last.extensions["timeout"]["read"] == amodb.DEFAULT_TIMEOUT == 15
    h2 = make(timeout=3)
    h2.run(lambda c: c.configuration())
    assert h2.last.extensions["timeout"] == {"connect": 3, "read": 3, "write": 3, "pool": 3}


# --- OMDb ---------------------------------------------------------------------

OMDB_ITEM = {"Title": "Fight Club", "Year": "1999", "imdbID": "tt0137523", "Response": "True"}


def test_omdb_by_id_sends_apikey_as_a_query_parameter(make: Make) -> None:
    h = make(ok(OMDB_ITEM))
    assert h.run(lambda c: c.omdb.by_id("tt0137523", plot="full")) == OMDB_ITEM
    assert str(h.last.url).startswith("https://api.amodb.dev/omdb/?")
    assert dict(h.last.url.params) == {"i": "tt0137523", "plot": "full", "apikey": KEY}
    assert "authorization" not in h.last.headers


def test_omdb_apikey_is_sent_in_query_auth_mode_too(make: Make) -> None:
    h = make(ok(OMDB_ITEM), auth="query")
    h.run(lambda c: c.omdb.by_id("tt0137523"))
    assert dict(h.last.url.params) == {"i": "tt0137523", "apikey": KEY}


def test_omdb_by_title(make: Make) -> None:
    h = make(ok(OMDB_ITEM))
    h.run(lambda c: c.omdb.by_title("Fight Club", type="movie", year=1999, plot="short"))
    assert dict(h.last.url.params) == {
        "t": "Fight Club",
        "type": "movie",
        "y": "1999",
        "plot": "short",
        "apikey": KEY,
    }


def test_omdb_search(make: Make) -> None:
    h = make(ok({"Search": [], "totalResults": "0", "Response": "True"}))
    h.run(lambda c: c.omdb.search("fight", type="movie", year=1999, page=2))
    assert dict(h.last.url.params) == {
        "s": "fight",
        "type": "movie",
        "y": "1999",
        "page": "2",
        "apikey": KEY,
    }


def test_omdb_accepts_a_params_dict(make: Make) -> None:
    h = make(ok(OMDB_ITEM))
    h.run(lambda c: c.omdb.by_id("tt0137523", params={"r": "json"}, plot="full"))
    assert dict(h.last.url.params) == {"i": "tt0137523", "plot": "full", "r": "json", "apikey": KEY}


def test_omdb_cannot_override_the_key(make: Make) -> None:
    h = make(ok(OMDB_ITEM))
    h.run(lambda c: c.omdb.by_id("tt0137523", apikey="other"))
    assert h.last.url.params.get_list("apikey") == [KEY]


def test_omdb_custom_url_without_trailing_slash(make: Make) -> None:
    h = make(ok(OMDB_ITEM), omdb_url="https://example.test/omdb")
    h.run(lambda c: c.omdb.by_id("tt0137523"))
    assert str(h.last.url) == f"https://example.test/omdb?i=tt0137523&apikey={KEY}"


def test_omdb_response_false_raises_amodb_error(make: Make) -> None:
    body = {"Response": "False", "Error": "Movie not found!"}
    h = make(ok(body))
    with pytest.raises(AmodbError) as info:
        h.run(lambda c: c.omdb.by_id("tt0000000"))
    err = info.value
    assert type(err) is AmodbError
    assert err.status == 200
    assert err.status_code is None
    assert err.status_message == "Movie not found!"
    assert err.body == body


def test_omdb_error_with_an_http_failure_status(make: Make) -> None:
    h = make(Reply(400, json={"Response": "False", "Error": "Format is not supported."}))
    with pytest.raises(AmodbError) as info:
        h.run(lambda c: c.omdb.by_id("tt0137523", r="xml"))
    assert info.value.status == 400
    assert info.value.status_message == "Format is not supported."


# --- images -------------------------------------------------------------------


def test_image_url(make: Make) -> None:
    h = make()

    def check(client: Any) -> None:
        assert client.image_url("/abc.jpg") == "https://img.amodb.dev/t/p/w500/abc.jpg"
        assert (
            client.image_url("/abc.jpg", "original") == "https://img.amodb.dev/t/p/original/abc.jpg"
        )
        assert client.image_url("abc.jpg", "w92") == "https://img.amodb.dev/t/p/w92/abc.jpg"
        assert client.image_url(None) is None
        assert client.image_url("") is None

    h.run(check)
    assert h.requests == []


def test_image_url_uses_the_configured_base(make: Make) -> None:
    h = make(image_base_url="https://cdn.example.test/img")
    assert (
        h.run(lambda c: c.image_url("/a.jpg", "w185")) == "https://cdn.example.test/img/w185/a.jpg"
    )


def test_module_level_image_url() -> None:
    assert amodb.image_url("/abc.jpg") == "https://img.amodb.dev/t/p/w500/abc.jpg"
    assert amodb.image_url("abc.jpg", "h632") == "https://img.amodb.dev/t/p/h632/abc.jpg"
    assert amodb.image_url(None) is None
    assert amodb.image_url("") is None
    assert amodb.image_url("/a.jpg", "w92", "https://x.test/p") == "https://x.test/p/w92/a.jpg"


# --- request, plans, misc -----------------------------------------------------


def test_request_escape_hatch_returns_parsed_json(make: Make) -> None:
    h = make(ok({"hello": "world"}))
    assert h.run(lambda c: c.request("/movie/550", {"language": "ru-RU"})) == {"hello": "world"}
    assert h.target == "/3/movie/550?language=ru-RU"
    assert h.last.headers["authorization"] == f"Bearer {KEY}"


def test_plans_uses_the_origin_of_the_base_url_and_sends_no_key(make: Make) -> None:
    body = {"currency": "USD", "plans": [{"id": "lite", "rpm": 20}]}
    h = make(ok(body))
    assert h.run(lambda c: c.plans()) == body
    assert str(h.last.url) == "https://api.amodb.dev/plans"
    assert "authorization" not in h.last.headers
    assert KEY not in str(h.last.url)


def test_plans_follows_a_custom_base_url(make: Make) -> None:
    h = make(base_url="http://localhost:8787/3")
    h.run(lambda c: c.plans())
    assert str(h.last.url) == "http://localhost:8787/plans"


def test_plans_never_sends_the_key_in_query_mode(make: Make) -> None:
    h = make(auth="query")
    h.run(lambda c: c.plans())
    assert h.last.url.query == b""


def test_errors_survive_pickling() -> None:
    import pickle

    err = RateLimitError("slow down", 429, 25, {"a": 1}, 7)
    copy = pickle.loads(pickle.dumps(err))
    assert isinstance(copy, RateLimitError)
    assert (copy.status, copy.status_code, copy.status_message, copy.body, copy.retry_after) == (
        429,
        25,
        "slow down",
        {"a": 1},
        7,
    )
    base = pickle.loads(pickle.dumps(AmodbError("x", 500, 11, "raw")))
    assert (base.status, base.status_code, base.body) == (500, 11, "raw")
