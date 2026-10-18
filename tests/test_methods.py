"""Every public method builds the expected path and query, on both clients."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

import pytest

from helpers import Runner

Call = Callable[[Any], Any]

CASES: list[tuple[str, Call, str]] = [
    # movies
    ("movies.details", lambda c: c.movies.details(550), "/3/movie/550"),
    (
        "movies.details+append",
        lambda c: c.movies.details(550, append_to_response=["credits", "images"]),
        "/3/movie/550?append_to_response=credits,images",
    ),
    (
        "movies.details+append-string",
        lambda c: c.movies.details(550, append_to_response="ratings,moods"),
        "/3/movie/550?append_to_response=ratings,moods",
    ),
    ("movies.credits", lambda c: c.movies.credits(550), "/3/movie/550/credits"),
    ("movies.images", lambda c: c.movies.images(550), "/3/movie/550/images"),
    ("movies.videos", lambda c: c.movies.videos(550), "/3/movie/550/videos"),
    ("movies.keywords", lambda c: c.movies.keywords(550), "/3/movie/550/keywords"),
    ("movies.external_ids", lambda c: c.movies.external_ids(550), "/3/movie/550/external_ids"),
    (
        "movies.recommendations",
        lambda c: c.movies.recommendations(550, 2),
        "/3/movie/550/recommendations?page=2",
    ),
    ("movies.similar", lambda c: c.movies.similar(550, page=3), "/3/movie/550/similar?page=3"),
    ("movies.reviews", lambda c: c.movies.reviews(550), "/3/movie/550/reviews"),
    ("movies.release_dates", lambda c: c.movies.release_dates(550), "/3/movie/550/release_dates"),
    (
        "movies.watch_providers",
        lambda c: c.movies.watch_providers(550),
        "/3/movie/550/watch/providers",
    ),
    ("movies.translations", lambda c: c.movies.translations(550), "/3/movie/550/translations"),
    (
        "movies.alternative_titles",
        lambda c: c.movies.alternative_titles(550),
        "/3/movie/550/alternative_titles",
    ),
    ("movies.popular", lambda c: c.movies.popular(), "/3/movie/popular"),
    ("movies.popular+page", lambda c: c.movies.popular(2), "/3/movie/popular?page=2"),
    (
        "movies.popular+region",
        lambda c: c.movies.popular(region="US"),
        "/3/movie/popular?region=US",
    ),
    ("movies.top_rated", lambda c: c.movies.top_rated(), "/3/movie/top_rated"),
    ("movies.upcoming", lambda c: c.movies.upcoming(), "/3/movie/upcoming"),
    ("movies.now_playing", lambda c: c.movies.now_playing(), "/3/movie/now_playing"),
    ("movies.moods", lambda c: c.movies.moods(550), "/3/movie/550/moods"),
    ("movies.soundtracks", lambda c: c.movies.soundtracks(550), "/3/movie/550/soundtracks"),
    ("movies.ratings", lambda c: c.movies.ratings(550), "/3/movie/550/ratings"),
    ("movies.wikidata", lambda c: c.movies.wikidata(550), "/3/movie/550/wikidata"),
    (
        "movies.showtimes",
        lambda c: c.movies.showtimes(550, "US"),
        "/3/movie/550/showtimes?country=US",
    ),
    # tv
    ("tv.details", lambda c: c.tv.details(1399), "/3/tv/1399"),
    (
        "tv.details+append",
        lambda c: c.tv.details(1399, append_to_response=["credits", "ratings"]),
        "/3/tv/1399?append_to_response=credits,ratings",
    ),
    (
        "tv.aggregate_credits",
        lambda c: c.tv.aggregate_credits(1399),
        "/3/tv/1399/aggregate_credits",
    ),
    ("tv.credits", lambda c: c.tv.credits(1399), "/3/tv/1399/credits"),
    ("tv.images", lambda c: c.tv.images(1399), "/3/tv/1399/images"),
    ("tv.videos", lambda c: c.tv.videos(1399), "/3/tv/1399/videos"),
    ("tv.keywords", lambda c: c.tv.keywords(1399), "/3/tv/1399/keywords"),
    ("tv.external_ids", lambda c: c.tv.external_ids(1399), "/3/tv/1399/external_ids"),
    (
        "tv.recommendations",
        lambda c: c.tv.recommendations(1399, 2),
        "/3/tv/1399/recommendations?page=2",
    ),
    ("tv.similar", lambda c: c.tv.similar(1399), "/3/tv/1399/similar"),
    ("tv.reviews", lambda c: c.tv.reviews(1399), "/3/tv/1399/reviews"),
    ("tv.content_ratings", lambda c: c.tv.content_ratings(1399), "/3/tv/1399/content_ratings"),
    (
        "tv.watch_providers",
        lambda c: c.tv.watch_providers(1399),
        "/3/tv/1399/watch/providers",
    ),
    ("tv.season", lambda c: c.tv.season(1399, 1), "/3/tv/1399/season/1"),
    (
        "tv.season+append",
        lambda c: c.tv.season(1399, 2, append_to_response=["credits"]),
        "/3/tv/1399/season/2?append_to_response=credits",
    ),
    ("tv.episode", lambda c: c.tv.episode(1399, 1, 2), "/3/tv/1399/season/1/episode/2"),
    ("tv.popular", lambda c: c.tv.popular(), "/3/tv/popular"),
    ("tv.top_rated", lambda c: c.tv.top_rated(4), "/3/tv/top_rated?page=4"),
    ("tv.airing_today", lambda c: c.tv.airing_today(), "/3/tv/airing_today"),
    ("tv.on_the_air", lambda c: c.tv.on_the_air(), "/3/tv/on_the_air"),
    ("tv.moods", lambda c: c.tv.moods(1399), "/3/tv/1399/moods"),
    ("tv.soundtracks", lambda c: c.tv.soundtracks(1399), "/3/tv/1399/soundtracks"),
    ("tv.ratings", lambda c: c.tv.ratings(1399), "/3/tv/1399/ratings"),
    ("tv.wikidata", lambda c: c.tv.wikidata(1399), "/3/tv/1399/wikidata"),
    # people
    ("people.details", lambda c: c.people.details(287), "/3/person/287"),
    (
        "people.combined_credits",
        lambda c: c.people.combined_credits(287),
        "/3/person/287/combined_credits",
    ),
    ("people.movie_credits", lambda c: c.people.movie_credits(287), "/3/person/287/movie_credits"),
    ("people.tv_credits", lambda c: c.people.tv_credits(287), "/3/person/287/tv_credits"),
    ("people.images", lambda c: c.people.images(287), "/3/person/287/images"),
    ("people.external_ids", lambda c: c.people.external_ids(287), "/3/person/287/external_ids"),
    ("people.popular", lambda c: c.people.popular(), "/3/person/popular"),
    # search
    ("search.movie", lambda c: c.search.movie("inception"), "/3/search/movie?query=inception"),
    ("search.tv", lambda c: c.search.tv("lost"), "/3/search/tv?query=lost"),
    ("search.person", lambda c: c.search.person("nolan"), "/3/search/person?query=nolan"),
    ("search.multi", lambda c: c.search.multi("alien"), "/3/search/multi?query=alien"),
    (
        "search.collection",
        lambda c: c.search.collection("bourne"),
        "/3/search/collection?query=bourne",
    ),
    ("search.company", lambda c: c.search.company("pixar"), "/3/search/company?query=pixar"),
    ("search.keyword", lambda c: c.search.keyword("heist"), "/3/search/keyword?query=heist"),
    (
        "search.movie+kwargs",
        lambda c: c.search.movie("a b&c", year=1999, page=2, include_adult=False),
        "/3/search/movie?query=a%20b%26c&year=1999&page=2&include_adult=false",
    ),
    (
        "search.movie+params-dict",
        lambda c: c.search.movie("x", {"primary_release_year": 2010}),
        "/3/search/movie?primary_release_year=2010&query=x",
    ),
    (
        "search.movie+cyrillic",
        lambda c: c.search.movie("Привет"),
        "/3/search/movie?query=%D0%9F%D1%80%D0%B8%D0%B2%D0%B5%D1%82",
    ),
    # discover
    ("discover.movie", lambda c: c.discover.movie(), "/3/discover/movie"),
    (
        "discover.movie+kwargs",
        lambda c: c.discover.movie(sort_by="popularity.desc", with_genres=[28, 12], page=2),
        "/3/discover/movie?sort_by=popularity.desc&with_genres=28,12&page=2",
    ),
    (
        "discover.movie+dotted-key",
        lambda c: c.discover.movie({"release_date.gte": date(2020, 1, 1)}),
        "/3/discover/movie?release_date.gte=2020-01-01",
    ),
    (
        "discover.movie+dotted-key-kwargs",
        lambda c: c.discover.movie(**{"vote_average.gte": 7.5}),
        "/3/discover/movie?vote_average.gte=7.5",
    ),
    ("discover.tv", lambda c: c.discover.tv(with_status=0), "/3/discover/tv?with_status=0"),
    # trending
    ("trending.get", lambda c: c.trending.get(), "/3/trending/all/day"),
    (
        "trending.get+movie-week",
        lambda c: c.trending.get("movie", "week"),
        "/3/trending/movie/week",
    ),
    ("trending.get+tv", lambda c: c.trending.get("tv"), "/3/trending/tv/day"),
    (
        "trending.get+person-page",
        lambda c: c.trending.get("person", "day", page=2),
        "/3/trending/person/day?page=2",
    ),
    # lists and single objects
    ("genres.movies", lambda c: c.genres.movies(), "/3/genre/movie/list"),
    ("genres.tv", lambda c: c.genres.tv(), "/3/genre/tv/list"),
    ("collections.details", lambda c: c.collections.details(10), "/3/collection/10"),
    ("companies.details", lambda c: c.companies.details(3), "/3/company/3"),
    ("networks.details", lambda c: c.networks.details(49), "/3/network/49"),
    ("keywords.details", lambda c: c.keywords.details(180547), "/3/keyword/180547"),
    # find, configuration, certifications, watch providers
    (
        "find",
        lambda c: c.find("tt0137523", "imdb_id"),
        "/3/find/tt0137523?external_source=imdb_id",
    ),
    (
        "find+second-source",
        lambda c: c.find("81189", "tvdb_id"),
        "/3/find/81189?external_source=tvdb_id",
    ),
    (
        "find+third-source",
        lambda c: c.find("Q190050", "wikidata_id"),
        "/3/find/Q190050?external_source=wikidata_id",
    ),
    (
        "find+fourth-source",
        lambda c: c.find("361", "kinopoisk_id"),
        "/3/find/361?external_source=kinopoisk_id",
    ),
    ("configuration", lambda c: c.configuration(), "/3/configuration"),
    ("certifications.movie", lambda c: c.certifications.movie(), "/3/certification/movie/list"),
    ("certifications.tv", lambda c: c.certifications.tv(), "/3/certification/tv/list"),
    (
        "watch_providers.regions",
        lambda c: c.watch_providers.regions(),
        "/3/watch/providers/regions",
    ),
    ("watch_providers.movie", lambda c: c.watch_providers.movie(), "/3/watch/providers/movie"),
    ("watch_providers.tv", lambda c: c.watch_providers.tv(), "/3/watch/providers/tv"),
    # the params dict is accepted by every method
    (
        "movies.popular+params-arg",
        lambda c: c.movies.popular(params={"region": "US", "page": 3}),
        "/3/movie/popular?region=US&page=3",
    ),
    (
        "movies.details+params-arg",
        lambda c: c.movies.details(550, params={"x.y": 1}),
        "/3/movie/550?x.y=1",
    ),
    (
        "find+params-arg",
        lambda c: c.find("tt1", "imdb_id", params={"language": "fr-FR"}),
        "/3/find/tt1?language=fr-FR&external_source=imdb_id",
    ),
    (
        "trending.get+params-arg",
        lambda c: c.trending.get("tv", "week", params={"page": 2}),
        "/3/trending/tv/week?page=2",
    ),
    # escape hatch
    ("request", lambda c: c.request("/movie/550"), "/3/movie/550"),
    (
        "request+params",
        lambda c: c.request("/movie/550", {"language": "ru-RU"}),
        "/3/movie/550?language=ru-RU",
    ),
]


@pytest.mark.parametrize(("name", "call", "target"), CASES, ids=[c[0] for c in CASES])
def test_method_builds_expected_request(
    make: Callable[..., Runner], name: str, call: Call, target: str
) -> None:
    runner = make()
    assert runner.run(call) == {"id": 1}
    assert len(runner.requests) == 1
    assert runner.last.method == "GET"
    assert runner.target == target


def test_every_case_name_is_unique() -> None:
    names = [c[0] for c in CASES]
    assert len(names) == len(set(names))


EXPECTED_METHODS: dict[str, set[str]] = {
    "movies": {
        "details",
        "credits",
        "images",
        "videos",
        "keywords",
        "external_ids",
        "recommendations",
        "similar",
        "reviews",
        "release_dates",
        "watch_providers",
        "translations",
        "alternative_titles",
        "popular",
        "top_rated",
        "upcoming",
        "now_playing",
        "moods",
        "soundtracks",
        "ratings",
        "wikidata",
        "showtimes",
    },
    "tv": {
        "details",
        "aggregate_credits",
        "credits",
        "images",
        "videos",
        "keywords",
        "external_ids",
        "recommendations",
        "similar",
        "reviews",
        "content_ratings",
        "watch_providers",
        "season",
        "episode",
        "popular",
        "top_rated",
        "airing_today",
        "on_the_air",
        "moods",
        "soundtracks",
        "ratings",
        "wikidata",
    },
    "people": {
        "details",
        "combined_credits",
        "movie_credits",
        "tv_credits",
        "images",
        "external_ids",
        "popular",
    },
    "search": {"movie", "tv", "person", "multi", "collection", "company", "keyword"},
    "discover": {"movie", "tv"},
    "trending": {"get"},
    "genres": {"movies", "tv"},
    "collections": {"details"},
    "companies": {"details"},
    "networks": {"details"},
    "keywords": {"details"},
    "certifications": {"movie", "tv"},
    "watch_providers": {"regions", "movie", "tv"},
    "omdb": {"by_id", "by_title", "search"},
}


def test_client_exposes_all_resources_and_methods(make: Callable[..., Runner]) -> None:
    def inspect_client(client: Any) -> dict[str, set[str]]:
        for name in ("find", "configuration", "plans", "image_url", "request"):
            assert callable(getattr(client, name))
        return {
            name: {m for m in dir(getattr(client, name)) if not m.startswith("_")}
            for name in EXPECTED_METHODS
        }

    assert make().run(inspect_client) == EXPECTED_METHODS


def test_every_tmdb_style_method_is_covered_by_a_case() -> None:
    covered = {c[0].split("+")[0] for c in CASES}
    for resource, methods in EXPECTED_METHODS.items():
        if resource == "omdb":
            continue
        for method in methods:
            assert f"{resource}.{method}" in covered, f"{resource}.{method} has no case"
