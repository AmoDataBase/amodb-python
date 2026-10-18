"""The amodb extension results: moods, soundtracks, ratings, wikidata, showtimes and find.

The files in ``tests/fixtures`` are real response bodies from the live API, cut short.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, get_args

import pytest

from amodb import AmodbError
from amodb import types as T
from helpers import Runner, ok, tmdb_error
from shapes import conforms

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10), reason="shapes.py reads X | None annotations"
)

Make = Callable[..., Runner]
FIXTURES = Path(__file__).parent / "fixtures"


def load(name: str) -> Any:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


# --- the types match real bodies ----------------------------------------------

FIXTURE_TYPES: list[tuple[str, Any]] = [
    ("moods_measured", T.Moods),
    ("moods_estimated", T.Moods),
    ("moods_empty", T.Moods),
    ("soundtracks_musicbrainz", T.Soundtracks),
    ("soundtracks_deezer", T.Soundtracks),
    ("soundtracks_empty", T.Soundtracks),
    ("ratings", T.Ratings),
    ("wikidata_movie", T.Wikidata),
    ("wikidata_follows", T.Wikidata),
    ("wikidata_based_on", T.Wikidata),
    ("showtimes_summary", T.Showtimes),
    ("showtimes_country", T.Showtimes),
    ("find_movie", T.FindResults),
    ("find_person", T.FindResults),
    ("find_tv", T.FindResults),
    ("external_ids_movie", T.MovieExternalIds),
    ("external_ids_tv", T.TvExternalIds),
    ("external_ids_person", T.PersonExternalIds),
    ("movie_appended", T.MovieDetails),
]


@pytest.mark.parametrize(("name", "shape"), FIXTURE_TYPES, ids=[n for n, _ in FIXTURE_TYPES])
def test_real_body_matches_the_declared_type(name: str, shape: Any) -> None:
    assert conforms(load(name), shape) == []


def test_appended_sections_have_no_id_except_wikidata_and_showtimes() -> None:
    body = load("movie_appended")
    assert conforms(body["moods"], T.MoodsSection) == []
    assert conforms(body["soundtracks"], T.SoundtracksSection) == []
    assert conforms(body["ratings"], T.RatingsSection) == []
    assert conforms(body["wikidata"], T.Wikidata) == []
    assert conforms(body["showtimes"], T.Showtimes) == []
    assert conforms(body["external_ids"], T.MovieExternalIds) == []
    for name in ("moods", "soundtracks", "ratings"):
        assert "id" not in body[name]
    assert body["wikidata"]["id"] == 550
    assert body["showtimes"]["id"] == 550


def test_the_checker_rejects_the_old_guessed_shapes() -> None:
    guessed_moods = {"id": 550, "moods": [{"name": "action", "value": 70}]}
    assert conforms(guessed_moods, T.Moods)
    assert conforms({"id": 550, "source": "measured", "results": [{"name": "a"}]}, T.Moods)
    assert conforms({"id": 550, "source": "guessed", "results": []}, T.Moods)
    assert conforms({"id": 550, "imdb": 8.8}, T.Ratings)
    assert conforms({"id": 550, "country": "US", "results": []}, T.Showtimes)
    assert conforms({"id": 550, "country": None, "results": [], "countries": [{}]}, T.Showtimes)


# --- what the fixtures say ---------------------------------------------------


def test_moods_scale_and_source() -> None:
    measured = load("moods_measured")
    assert measured["source"] == "measured"
    names = [m["name"] for m in measured["results"]]
    assert names == sorted(names)
    for mood in measured["results"]:
        assert 0 <= mood["avg"] <= 10
        assert all(0 <= value <= 10 for value in mood["values"])
    estimated = load("moods_estimated")
    assert estimated["source"] == "estimated"
    assert all(float(m["avg"]).is_integer() for m in estimated["results"])
    empty = load("moods_empty")
    assert empty["source"] is None
    assert empty["results"] == []


def test_ratings_providers() -> None:
    ratings = load("ratings")
    assert list(ratings) == ["id", "imdb", "kinopoisk", "metacritic", "rotten_tomatoes", "tmdb"]
    assert ratings["imdb"] == {"value": 8.8, "votes": 2669989}
    assert ratings["kinopoisk"]["votes"] is None
    assert ratings["metacritic"]["value"] <= 100
    assert ratings["tmdb"]["value"] <= 10


def test_soundtracks_albums_and_tracks() -> None:
    album = load("soundtracks_musicbrainz")["results"][0]
    assert album["source"] == "musicbrainz"
    assert set(album["tracks"][0]) == {"disc", "number", "title", "artist", "duration_ms"}
    assert load("soundtracks_deezer")["results"][0]["source"] == "deezer"
    assert load("soundtracks_empty")["results"] == []


def test_wikidata_money_and_links() -> None:
    movie = load("wikidata_movie")
    assert movie["budget"] == {"value": 63000000, "currency": "USD"}
    assert movie["box_office"]["worldwide"] is True
    assert "worldwide" not in movie["budget"]
    assert movie["sitelinks"]["en"] == "Fight Club"
    assert movie["based_on"][0]["author"]["label"] == "Chuck Palahniuk"
    assert "year" not in movie["awards"][0]
    assert isinstance(movie["awards"][1]["year"], int)
    follows = load("wikidata_follows")
    assert follows["followed_by"]["media_type"] in ("movie", "tv")
    assert isinstance(follows["followed_by"]["tmdb_id"], int)


def test_showtimes_without_and_with_a_country() -> None:
    summary = load("showtimes_summary")
    assert summary["country"] is None
    assert summary["results"] == []
    row = summary["countries"][0]
    assert set(row) == {"country", "name", "venues", "cities", "showtimes", "first_day", "last_day"}
    full = load("showtimes_country")
    assert full["country"] == "RU"
    venue = full["results"][0]
    assert venue["chain"]["key"]
    assert venue["showtimes"][0]["start"].startswith(venue["showtimes"][0]["date"])
    assert full["countries"][0]["country"] == "RU"


def test_find_results_keep_the_media_type() -> None:
    movie = load("find_movie")
    assert movie["movie_results"][0]["media_type"] == "movie"
    assert movie["tv_episode_results"] == []
    assert movie["tv_season_results"] == []
    assert load("find_person")["person_results"][0]["media_type"] == "person"
    assert load("find_tv")["tv_results"][0]["media_type"] == "tv"


def test_kinopoisk_id_is_a_string() -> None:
    assert load("external_ids_movie")["kinopoisk_id"] == "361"
    assert load("external_ids_tv")["kinopoisk_id"] == "404900"
    assert "kinopoisk_id" not in load("external_ids_person")


# --- the clients return those bodies unchanged --------------------------------

CALLS: list[tuple[str, Callable[[Any], Any], str, Any, str]] = [
    (
        "movies.moods",
        lambda c: c.movies.moods(155),
        "moods_measured",
        T.Moods,
        "/3/movie/155/moods",
    ),
    ("tv.moods", lambda c: c.tv.moods(1396), "moods_estimated", T.Moods, "/3/tv/1396/moods"),
    (
        "movies.soundtracks",
        lambda c: c.movies.soundtracks(155),
        "soundtracks_musicbrainz",
        T.Soundtracks,
        "/3/movie/155/soundtracks",
    ),
    (
        "tv.soundtracks",
        lambda c: c.tv.soundtracks(1396),
        "soundtracks_empty",
        T.Soundtracks,
        "/3/tv/1396/soundtracks",
    ),
    (
        "movies.ratings",
        lambda c: c.movies.ratings(550),
        "ratings",
        T.Ratings,
        "/3/movie/550/ratings",
    ),
    (
        "movies.wikidata",
        lambda c: c.movies.wikidata(550),
        "wikidata_movie",
        T.Wikidata,
        "/3/movie/550/wikidata",
    ),
    (
        "movies.showtimes",
        lambda c: c.movies.showtimes(550),
        "showtimes_summary",
        T.Showtimes,
        "/3/movie/550/showtimes",
    ),
    (
        "movies.showtimes+country",
        lambda c: c.movies.showtimes(550, "RU"),
        "showtimes_country",
        T.Showtimes,
        "/3/movie/550/showtimes?country=RU",
    ),
    (
        "find",
        lambda c: c.find("tt0137523", "imdb_id"),
        "find_movie",
        T.FindResults,
        "/3/find/tt0137523?external_source=imdb_id",
    ),
    (
        "find+kinopoisk",
        lambda c: c.find("361", "kinopoisk_id"),
        "find_movie",
        T.FindResults,
        "/3/find/361?external_source=kinopoisk_id",
    ),
    (
        "movies.external_ids",
        lambda c: c.movies.external_ids(550),
        "external_ids_movie",
        T.MovieExternalIds,
        "/3/movie/550/external_ids",
    ),
]


@pytest.mark.parametrize(
    ("call", "name", "shape", "target"),
    [case[1:] for case in CALLS],
    ids=[case[0] for case in CALLS],
)
def test_client_returns_the_body_as_is(
    make: Make, call: Callable[[Any], Any], name: str, shape: Any, target: str
) -> None:
    body = load(name)
    runner = make(ok(body))
    assert runner.run(call) == body
    assert runner.target == target
    assert conforms(runner.run(call), shape) == []


def test_showtimes_country_is_optional_and_can_be_a_region(make: Make) -> None:
    runner = make(ok(load("showtimes_summary")))
    result = runner.run(lambda c: c.movies.showtimes(550))
    assert "country" not in runner.last.url.params
    assert result["country"] is None
    assert result["countries"][0]["country"] == "RU"
    runner.run(lambda c: c.movies.showtimes(550, region="RU"))
    assert runner.last.url.params["region"] == "RU"
    assert "country" not in runner.last.url.params


def test_showtimes_can_be_appended_with_a_country(make: Make) -> None:
    runner = make(ok(load("movie_appended")))
    runner.run(lambda c: c.movies.details(550, append_to_response="showtimes", country="RU"))
    assert runner.target == "/3/movie/550?append_to_response=showtimes&country=RU"


def test_every_extension_value_can_be_appended(make: Make) -> None:
    names = ["ratings", "moods", "soundtracks", "wikidata", "showtimes"]
    runner = make(ok(load("movie_appended")))
    body = runner.run(lambda c: c.movies.details(550, append_to_response=names))
    assert runner.last.url.params["append_to_response"] == ",".join(names)
    assert conforms(body, T.MovieDetails) == []


# --- find sources --------------------------------------------------------------

FIND_SOURCES = [
    "imdb_id",
    "freebase_mid",
    "freebase_id",
    "tvdb_id",
    "tvrage_id",
    "facebook_id",
    "twitter_id",
    "instagram_id",
    "tiktok_id",
    "youtube_id",
    "wikidata_id",
    "kinopoisk_id",
]


def test_external_source_type_lists_every_source() -> None:
    assert list(get_args(T.ExternalSource)) == FIND_SOURCES


@pytest.mark.parametrize("source", FIND_SOURCES)
def test_find_sends_every_external_source(make: Make, source: str) -> None:
    runner = make(ok(load("find_movie")))
    runner.run(lambda c: c.find("123", source))
    assert runner.target == f"/3/find/123?external_source={source}"


# --- errors and removed methods ---------------------------------------------------


ROUTES: dict[str, Callable[[Any], Any]] = {
    "movies.moods": lambda c: c.movies.moods(1),
    "movies.soundtracks": lambda c: c.movies.soundtracks(1),
    "movies.ratings": lambda c: c.movies.ratings(1),
    "movies.wikidata": lambda c: c.movies.wikidata(1),
    "movies.showtimes": lambda c: c.movies.showtimes(1),
    "tv.moods": lambda c: c.tv.moods(1),
    "tv.soundtracks": lambda c: c.tv.soundtracks(1),
    "tv.ratings": lambda c: c.tv.ratings(1),
    "tv.wikidata": lambda c: c.tv.wikidata(1),
    "tv.showtimes": lambda c: c.tv.showtimes(1, "US"),
}


@pytest.mark.parametrize("call", list(ROUTES.values()), ids=list(ROUTES))
def test_extension_routes_keep_the_404_mapping(make: Make, call: Callable[[Any], Any]) -> None:
    message = "The resource you requested could not be found."
    runner = make(tmdb_error(404, 34, message))
    with pytest.raises(AmodbError) as info:
        runner.run(call)
    assert info.value.status == 404
    assert info.value.status_code == 34
    assert info.value.status_message == message


def test_methods_for_paths_the_api_does_not_offer_are_gone(make: Make) -> None:
    gone_on_resources = {
        "movies": ["aggregate_credits", "changes", "content_ratings"],
        "tv": ["aggregate_credits", "changes", "release_dates", "screened_theatrically"],
        "people": ["changes", "translations", "tagged_images", "latest"],
        "collections": ["images", "translations"],
        "companies": ["images", "alternative_names"],
        "networks": ["images", "alternative_names"],
    }
    gone_on_client = ["account", "authentication", "guest_sessions", "lists", "credits", "reviews"]

    def inspect_client(client: Any) -> list[str]:
        found = [
            f"{resource}.{method}"
            for resource, methods in gone_on_resources.items()
            for method in methods
            if hasattr(getattr(client, resource), method)
        ]
        return found + [name for name in gone_on_client if hasattr(client, name)]

    assert make().run(inspect_client) == []
