"""Resource classes and the API surface shared by Client and AsyncClient.

Each method is a one or two line wrapper: it builds ``(path, params)`` with
``_endpoints.build`` and passes the pair to the client's ``request``. The classes are
generic over the return type ``R``. The sync client uses ``R = dict`` and the async
client uses ``R = Coroutine[..., dict]``, so one copy of every method serves both.

Every method accepts ``language`` and any other keyword as a query parameter. A
``params={...}`` dict adds parameters whose names are not valid Python identifiers,
such as ``release_date.gte``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any, Generic, Literal, TypeVar

from . import _endpoints as ep
from ._core import Settings

R = TypeVar("R")

ExternalSource = Literal["imdb_id", "tvdb_id", "wikidata_id", "kinopoisk_id"]
MediaType = Literal["all", "movie", "tv", "person"]
TimeWindow = Literal["day", "week"]


class _Resource(Generic[R]):
    def __init__(self, send: Callable[[str, Mapping[str, Any] | None], R]) -> None:
        self._send = send

    def _get(self, template: str, *segments: object, **params: Any) -> R:
        path, query = ep.build(template, *segments, **params)
        return self._send(path, query)


class Movies(_Resource[R]):
    """Movie endpoints."""

    def details(
        self,
        id: int,
        *,
        append_to_response: Sequence[str] | str | None = None,
        language: str | None = None,
        **params: Any,
    ) -> R:
        return self._get(
            "/movie/{}", id, append_to_response=append_to_response, language=language, **params
        )

    def credits(self, id: int, *, language: str | None = None, **params: Any) -> R:
        return self._get("/movie/{}/credits", id, language=language, **params)

    def images(self, id: int, *, language: str | None = None, **params: Any) -> R:
        return self._get("/movie/{}/images", id, language=language, **params)

    def videos(self, id: int, *, language: str | None = None, **params: Any) -> R:
        return self._get("/movie/{}/videos", id, language=language, **params)

    def keywords(self, id: int, **params: Any) -> R:
        return self._get("/movie/{}/keywords", id, **params)

    def external_ids(self, id: int, **params: Any) -> R:
        return self._get("/movie/{}/external_ids", id, **params)

    def recommendations(
        self, id: int, page: int | None = None, *, language: str | None = None, **params: Any
    ) -> R:
        return self._get("/movie/{}/recommendations", id, page=page, language=language, **params)

    def similar(
        self, id: int, page: int | None = None, *, language: str | None = None, **params: Any
    ) -> R:
        return self._get("/movie/{}/similar", id, page=page, language=language, **params)

    def reviews(
        self, id: int, page: int | None = None, *, language: str | None = None, **params: Any
    ) -> R:
        return self._get("/movie/{}/reviews", id, page=page, language=language, **params)

    def release_dates(self, id: int, **params: Any) -> R:
        return self._get("/movie/{}/release_dates", id, **params)

    def watch_providers(self, id: int, **params: Any) -> R:
        return self._get("/movie/{}/watch/providers", id, **params)

    def translations(self, id: int, **params: Any) -> R:
        return self._get("/movie/{}/translations", id, **params)

    def alternative_titles(self, id: int, **params: Any) -> R:
        return self._get("/movie/{}/alternative_titles", id, **params)

    def popular(self, page: int | None = None, *, language: str | None = None, **params: Any) -> R:
        return self._get("/movie/popular", page=page, language=language, **params)

    def top_rated(
        self, page: int | None = None, *, language: str | None = None, **params: Any
    ) -> R:
        return self._get("/movie/top_rated", page=page, language=language, **params)

    def upcoming(self, page: int | None = None, *, language: str | None = None, **params: Any) -> R:
        return self._get("/movie/upcoming", page=page, language=language, **params)

    def now_playing(
        self, page: int | None = None, *, language: str | None = None, **params: Any
    ) -> R:
        return self._get("/movie/now_playing", page=page, language=language, **params)

    # amodb extras

    def moods(self, id: int, **params: Any) -> R:
        return self._get("/movie/{}/moods", id, **params)

    def soundtracks(self, id: int, **params: Any) -> R:
        return self._get("/movie/{}/soundtracks", id, **params)

    def ratings(self, id: int, **params: Any) -> R:
        return self._get("/movie/{}/ratings", id, **params)

    def wikidata(self, id: int, **params: Any) -> R:
        return self._get("/movie/{}/wikidata", id, **params)

    def showtimes(self, id: int, country: str | None = None, **params: Any) -> R:
        return self._get("/movie/{}/showtimes", id, country=country, **params)


class Tv(_Resource[R]):
    """TV show endpoints."""

    def details(
        self,
        id: int,
        *,
        append_to_response: Sequence[str] | str | None = None,
        language: str | None = None,
        **params: Any,
    ) -> R:
        return self._get(
            "/tv/{}", id, append_to_response=append_to_response, language=language, **params
        )

    def aggregate_credits(self, id: int, *, language: str | None = None, **params: Any) -> R:
        return self._get("/tv/{}/aggregate_credits", id, language=language, **params)

    def credits(self, id: int, *, language: str | None = None, **params: Any) -> R:
        return self._get("/tv/{}/credits", id, language=language, **params)

    def images(self, id: int, *, language: str | None = None, **params: Any) -> R:
        return self._get("/tv/{}/images", id, language=language, **params)

    def videos(self, id: int, *, language: str | None = None, **params: Any) -> R:
        return self._get("/tv/{}/videos", id, language=language, **params)

    def keywords(self, id: int, **params: Any) -> R:
        return self._get("/tv/{}/keywords", id, **params)

    def external_ids(self, id: int, **params: Any) -> R:
        return self._get("/tv/{}/external_ids", id, **params)

    def recommendations(
        self, id: int, page: int | None = None, *, language: str | None = None, **params: Any
    ) -> R:
        return self._get("/tv/{}/recommendations", id, page=page, language=language, **params)

    def similar(
        self, id: int, page: int | None = None, *, language: str | None = None, **params: Any
    ) -> R:
        return self._get("/tv/{}/similar", id, page=page, language=language, **params)

    def reviews(
        self, id: int, page: int | None = None, *, language: str | None = None, **params: Any
    ) -> R:
        return self._get("/tv/{}/reviews", id, page=page, language=language, **params)

    def content_ratings(self, id: int, **params: Any) -> R:
        return self._get("/tv/{}/content_ratings", id, **params)

    def watch_providers(self, id: int, **params: Any) -> R:
        return self._get("/tv/{}/watch/providers", id, **params)

    def season(
        self,
        tv_id: int,
        season_number: int,
        *,
        append_to_response: Sequence[str] | str | None = None,
        language: str | None = None,
        **params: Any,
    ) -> R:
        return self._get(
            "/tv/{}/season/{}",
            tv_id,
            season_number,
            append_to_response=append_to_response,
            language=language,
            **params,
        )

    def episode(
        self,
        tv_id: int,
        season_number: int,
        episode_number: int,
        *,
        append_to_response: Sequence[str] | str | None = None,
        language: str | None = None,
        **params: Any,
    ) -> R:
        return self._get(
            "/tv/{}/season/{}/episode/{}",
            tv_id,
            season_number,
            episode_number,
            append_to_response=append_to_response,
            language=language,
            **params,
        )

    def popular(self, page: int | None = None, *, language: str | None = None, **params: Any) -> R:
        return self._get("/tv/popular", page=page, language=language, **params)

    def top_rated(
        self, page: int | None = None, *, language: str | None = None, **params: Any
    ) -> R:
        return self._get("/tv/top_rated", page=page, language=language, **params)

    def airing_today(
        self, page: int | None = None, *, language: str | None = None, **params: Any
    ) -> R:
        return self._get("/tv/airing_today", page=page, language=language, **params)

    def on_the_air(
        self, page: int | None = None, *, language: str | None = None, **params: Any
    ) -> R:
        return self._get("/tv/on_the_air", page=page, language=language, **params)

    # amodb extras

    def moods(self, id: int, **params: Any) -> R:
        return self._get("/tv/{}/moods", id, **params)

    def soundtracks(self, id: int, **params: Any) -> R:
        return self._get("/tv/{}/soundtracks", id, **params)

    def ratings(self, id: int, **params: Any) -> R:
        return self._get("/tv/{}/ratings", id, **params)

    def wikidata(self, id: int, **params: Any) -> R:
        return self._get("/tv/{}/wikidata", id, **params)


class People(_Resource[R]):
    """Person endpoints."""

    def details(
        self,
        id: int,
        *,
        append_to_response: Sequence[str] | str | None = None,
        language: str | None = None,
        **params: Any,
    ) -> R:
        return self._get(
            "/person/{}", id, append_to_response=append_to_response, language=language, **params
        )

    def combined_credits(self, id: int, *, language: str | None = None, **params: Any) -> R:
        return self._get("/person/{}/combined_credits", id, language=language, **params)

    def movie_credits(self, id: int, *, language: str | None = None, **params: Any) -> R:
        return self._get("/person/{}/movie_credits", id, language=language, **params)

    def tv_credits(self, id: int, *, language: str | None = None, **params: Any) -> R:
        return self._get("/person/{}/tv_credits", id, language=language, **params)

    def images(self, id: int, **params: Any) -> R:
        return self._get("/person/{}/images", id, **params)

    def external_ids(self, id: int, **params: Any) -> R:
        return self._get("/person/{}/external_ids", id, **params)

    def popular(self, page: int | None = None, *, language: str | None = None, **params: Any) -> R:
        return self._get("/person/popular", page=page, language=language, **params)


class Search(_Resource[R]):
    """Search endpoints. Pass ``page=2``, ``year=1999`` and similar as keywords."""

    def movie(
        self,
        query: str,
        params: Mapping[str, Any] | None = None,
        *,
        language: str | None = None,
        **extra: Any,
    ) -> R:
        return self._get("/search/movie", query=query, params=params, language=language, **extra)

    def tv(
        self,
        query: str,
        params: Mapping[str, Any] | None = None,
        *,
        language: str | None = None,
        **extra: Any,
    ) -> R:
        return self._get("/search/tv", query=query, params=params, language=language, **extra)

    def person(
        self,
        query: str,
        params: Mapping[str, Any] | None = None,
        *,
        language: str | None = None,
        **extra: Any,
    ) -> R:
        return self._get("/search/person", query=query, params=params, language=language, **extra)

    def multi(
        self,
        query: str,
        params: Mapping[str, Any] | None = None,
        *,
        language: str | None = None,
        **extra: Any,
    ) -> R:
        return self._get("/search/multi", query=query, params=params, language=language, **extra)

    def collection(
        self,
        query: str,
        params: Mapping[str, Any] | None = None,
        *,
        language: str | None = None,
        **extra: Any,
    ) -> R:
        return self._get(
            "/search/collection", query=query, params=params, language=language, **extra
        )

    def company(
        self,
        query: str,
        params: Mapping[str, Any] | None = None,
        *,
        language: str | None = None,
        **extra: Any,
    ) -> R:
        return self._get("/search/company", query=query, params=params, language=language, **extra)

    def keyword(
        self,
        query: str,
        params: Mapping[str, Any] | None = None,
        *,
        language: str | None = None,
        **extra: Any,
    ) -> R:
        return self._get("/search/keyword", query=query, params=params, language=language, **extra)


class Discover(_Resource[R]):
    """Discover endpoints. Filters are keywords, for example ``with_genres=[28, 12]``."""

    def movie(
        self,
        params: Mapping[str, Any] | None = None,
        *,
        language: str | None = None,
        **extra: Any,
    ) -> R:
        return self._get("/discover/movie", params=params, language=language, **extra)

    def tv(
        self,
        params: Mapping[str, Any] | None = None,
        *,
        language: str | None = None,
        **extra: Any,
    ) -> R:
        return self._get("/discover/tv", params=params, language=language, **extra)


class Trending(_Resource[R]):
    """Trending endpoint."""

    def get(
        self,
        media_type: MediaType = "all",
        window: TimeWindow = "day",
        params: Mapping[str, Any] | None = None,
        *,
        language: str | None = None,
        **extra: Any,
    ) -> R:
        return self._get(
            "/trending/{}/{}", media_type, window, params=params, language=language, **extra
        )


class Genres(_Resource[R]):
    """Genre lists."""

    def movies(self, *, language: str | None = None, **params: Any) -> R:
        return self._get("/genre/movie/list", language=language, **params)

    def tv(self, *, language: str | None = None, **params: Any) -> R:
        return self._get("/genre/tv/list", language=language, **params)


class Collections(_Resource[R]):
    def details(self, id: int, *, language: str | None = None, **params: Any) -> R:
        return self._get("/collection/{}", id, language=language, **params)


class Companies(_Resource[R]):
    def details(self, id: int, **params: Any) -> R:
        return self._get("/company/{}", id, **params)


class Networks(_Resource[R]):
    def details(self, id: int, **params: Any) -> R:
        return self._get("/network/{}", id, **params)


class Keywords(_Resource[R]):
    def details(self, id: int, **params: Any) -> R:
        return self._get("/keyword/{}", id, **params)


class Certifications(_Resource[R]):
    """Age rating lists."""

    def movie(self, **params: Any) -> R:
        return self._get("/certification/movie/list", **params)

    def tv(self, **params: Any) -> R:
        return self._get("/certification/tv/list", **params)


class WatchProviders(_Resource[R]):
    """Streaming provider lists."""

    def regions(self, *, language: str | None = None, **params: Any) -> R:
        return self._get("/watch/providers/regions", language=language, **params)

    def movie(self, *, language: str | None = None, **params: Any) -> R:
        return self._get("/watch/providers/movie", language=language, **params)

    def tv(self, *, language: str | None = None, **params: Any) -> R:
        return self._get("/watch/providers/tv", language=language, **params)


class Omdb(Generic[R]):
    """OMDb compatible endpoint. The key is sent as ``apikey``."""

    def __init__(self, send: Callable[[Mapping[str, Any]], R]) -> None:
        self._send = send

    def by_id(
        self,
        imdb_id: str,
        *,
        plot: Literal["short", "full"] | None = None,
        type: Literal["movie", "series", "episode"] | None = None,
        year: int | str | None = None,
        **params: Any,
    ) -> R:
        return self._send(
            ep.merge(
                {"i": imdb_id, "plot": plot, "type": type, "y": year},
                params.pop("params", None),
                params,
            )
        )

    def by_title(
        self,
        title: str,
        *,
        type: Literal["movie", "series", "episode"] | None = None,
        year: int | str | None = None,
        plot: Literal["short", "full"] | None = None,
        **params: Any,
    ) -> R:
        return self._send(
            ep.merge(
                {"t": title, "type": type, "y": year, "plot": plot},
                params.pop("params", None),
                params,
            )
        )

    def search(
        self,
        query: str,
        *,
        type: Literal["movie", "series", "episode"] | None = None,
        year: int | str | None = None,
        page: int | None = None,
        **params: Any,
    ) -> R:
        return self._send(
            ep.merge(
                {"s": query, "type": type, "y": year, "page": page},
                params.pop("params", None),
                params,
            )
        )


class ClientApi(Generic[R]):
    """The public surface shared by ``Client`` and ``AsyncClient``.

    A subclass sets ``_settings``, implements ``request``, ``_omdb`` and ``_plans``,
    and calls ``_init_api`` once.
    """

    _settings: Settings

    movies: Movies[R]
    tv: Tv[R]
    people: People[R]
    search: Search[R]
    discover: Discover[R]
    trending: Trending[R]
    genres: Genres[R]
    collections: Collections[R]
    companies: Companies[R]
    networks: Networks[R]
    keywords: Keywords[R]
    certifications: Certifications[R]
    watch_providers: WatchProviders[R]
    omdb: Omdb[R]

    def _init_api(self) -> None:
        self.movies = Movies(self.request)
        self.tv = Tv(self.request)
        self.people = People(self.request)
        self.search = Search(self.request)
        self.discover = Discover(self.request)
        self.trending = Trending(self.request)
        self.genres = Genres(self.request)
        self.collections = Collections(self.request)
        self.companies = Companies(self.request)
        self.networks = Networks(self.request)
        self.keywords = Keywords(self.request)
        self.certifications = Certifications(self.request)
        self.watch_providers = WatchProviders(self.request)
        self.omdb = Omdb(self._omdb)

    def request(self, path: str, params: Mapping[str, Any] | None = None) -> R:
        """GET ``base_url + path`` with auth, retry and error handling. Returns parsed JSON."""
        raise NotImplementedError

    def _omdb(self, params: Mapping[str, Any]) -> R:
        raise NotImplementedError

    def _plans(self) -> R:
        raise NotImplementedError

    def find(
        self,
        external_id: str,
        external_source: ExternalSource,
        *,
        language: str | None = None,
        **params: Any,
    ) -> R:
        """Look up a title or person by an external id such as an IMDb id."""
        return self.request(
            *ep.build(
                "/find/{}",
                external_id,
                external_source=external_source,
                language=language,
                **params,
            )
        )

    def configuration(self, **params: Any) -> R:
        """Image base URLs and the size lists."""
        return self.request(*ep.build("/configuration", **params))

    def plans(self) -> R:
        """Public plan list with requests per minute and live prices. No key is sent."""
        return self._plans()

    def image_url(self, path: str | None, size: str = "w500") -> str | None:
        """Full image URL for a ``poster_path`` style value. None for an empty path."""
        return ep.image_url(path, size, self._settings.image_base_url)
