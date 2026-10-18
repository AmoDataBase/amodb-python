"""Typed dictionaries for the main response objects.

Every client method returns a plain ``dict``. These classes describe the common
shapes so you can annotate your own code. Each one is ``total=False`` because the
API leaves out fields that are unknown. Use ``typing.cast`` to apply one::

    from typing import cast
    from amodb.types import MovieDetails

    movie = cast(MovieDetails, client.movies.details(550))
"""

from __future__ import annotations

from typing import Any, TypedDict

__all__ = [
    "Cast",
    "Configuration",
    "Credits",
    "Crew",
    "Episode",
    "ErrorBody",
    "FindResults",
    "Genre",
    "Image",
    "Images",
    "ImagesConfiguration",
    "MovieDetails",
    "MoviePage",
    "MovieSummary",
    "OmdbItem",
    "OmdbRating",
    "OmdbSearch",
    "OmdbSearchHit",
    "PersonDetails",
    "PersonPage",
    "PersonSummary",
    "Plan",
    "PlanPeriod",
    "Plans",
    "RatingValue",
    "Ratings",
    "SeasonDetails",
    "SeasonSummary",
    "SearchPage",
    "TvDetails",
    "TvPage",
    "TvSummary",
    "Video",
    "Videos",
]


class Genre(TypedDict, total=False):
    id: int
    name: str


class ProductionCompany(TypedDict, total=False):
    id: int
    logo_path: str | None
    name: str
    origin_country: str


class ProductionCountry(TypedDict, total=False):
    iso_3166_1: str
    name: str


class SpokenLanguage(TypedDict, total=False):
    english_name: str
    iso_639_1: str
    name: str


class Cast(TypedDict, total=False):
    id: int
    name: str
    original_name: str
    character: str
    credit_id: str
    order: int
    profile_path: str | None


class Crew(TypedDict, total=False):
    id: int
    name: str
    original_name: str
    department: str
    job: str
    credit_id: str
    profile_path: str | None


class Credits(TypedDict, total=False):
    id: int
    cast: list[Cast]
    crew: list[Crew]


class Image(TypedDict, total=False):
    file_path: str
    width: int
    height: int
    aspect_ratio: float
    iso_639_1: str | None
    vote_average: float
    vote_count: int


class Images(TypedDict, total=False):
    id: int
    backdrops: list[Image]
    logos: list[Image]
    posters: list[Image]
    profiles: list[Image]
    stills: list[Image]


class Video(TypedDict, total=False):
    id: str
    key: str
    name: str
    site: str
    type: str
    official: bool
    size: int
    published_at: str
    iso_639_1: str
    iso_3166_1: str


class Videos(TypedDict, total=False):
    id: int
    results: list[Video]


class RatingValue(TypedDict, total=False):
    value: float | int | None
    votes: int | None


class Ratings(TypedDict, total=False):
    """Result of ``movies.ratings`` and ``tv.ratings``. Each source can be None."""

    imdb: RatingValue | None
    kinopoisk: RatingValue | None
    metacritic: RatingValue | None
    rotten_tomatoes: RatingValue | None
    tmdb: RatingValue | None


class MovieSummary(TypedDict, total=False):
    adult: bool
    backdrop_path: str | None
    genre_ids: list[int]
    id: int
    original_language: str
    original_title: str
    overview: str
    popularity: float
    poster_path: str | None
    release_date: str
    title: str
    video: bool
    vote_average: float
    vote_count: int


class MovieDetails(TypedDict, total=False):
    adult: bool
    backdrop_path: str | None
    belongs_to_collection: dict[str, Any] | None
    budget: int
    genres: list[Genre]
    homepage: str | None
    id: int
    imdb_id: str | None
    original_language: str
    original_title: str
    overview: str | None
    popularity: float
    poster_path: str | None
    production_companies: list[ProductionCompany]
    production_countries: list[ProductionCountry]
    release_date: str
    revenue: int
    runtime: int | None
    spoken_languages: list[SpokenLanguage]
    status: str
    tagline: str | None
    title: str
    video: bool
    vote_average: float
    vote_count: int
    # Present only when requested with append_to_response.
    credits: Credits
    images: Images
    videos: Videos
    ratings: Ratings
    moods: dict[str, Any]
    soundtracks: dict[str, Any]
    wikidata: dict[str, Any]
    showtimes: dict[str, Any]


class TvSummary(TypedDict, total=False):
    backdrop_path: str | None
    first_air_date: str
    genre_ids: list[int]
    id: int
    name: str
    origin_country: list[str]
    original_language: str
    original_name: str
    overview: str
    popularity: float
    poster_path: str | None
    vote_average: float
    vote_count: int


class SeasonSummary(TypedDict, total=False):
    air_date: str | None
    episode_count: int
    id: int
    name: str
    overview: str
    poster_path: str | None
    season_number: int


class TvDetails(TypedDict, total=False):
    backdrop_path: str | None
    created_by: list[dict[str, Any]]
    episode_run_time: list[int]
    first_air_date: str
    genres: list[Genre]
    homepage: str
    id: int
    in_production: bool
    languages: list[str]
    last_air_date: str | None
    name: str
    number_of_episodes: int
    number_of_seasons: int
    origin_country: list[str]
    original_language: str
    original_name: str
    overview: str
    popularity: float
    poster_path: str | None
    seasons: list[SeasonSummary]
    status: str
    tagline: str
    type: str
    vote_average: float
    vote_count: int
    # Present only when requested with append_to_response.
    credits: Credits
    images: Images
    videos: Videos
    ratings: Ratings
    moods: dict[str, Any]
    soundtracks: dict[str, Any]
    wikidata: dict[str, Any]


class Episode(TypedDict, total=False):
    air_date: str | None
    episode_number: int
    id: int
    name: str
    overview: str
    runtime: int | None
    season_number: int
    still_path: str | None
    vote_average: float
    vote_count: int


class SeasonDetails(TypedDict, total=False):
    _id: str
    air_date: str | None
    episodes: list[Episode]
    id: int
    name: str
    overview: str
    poster_path: str | None
    season_number: int


class PersonSummary(TypedDict, total=False):
    adult: bool
    gender: int
    id: int
    known_for_department: str
    name: str
    original_name: str
    popularity: float
    profile_path: str | None


class PersonDetails(TypedDict, total=False):
    adult: bool
    also_known_as: list[str]
    biography: str
    birthday: str | None
    deathday: str | None
    gender: int
    homepage: str | None
    id: int
    imdb_id: str | None
    known_for_department: str
    name: str
    place_of_birth: str | None
    popularity: float
    profile_path: str | None


class MoviePage(TypedDict, total=False):
    page: int
    results: list[MovieSummary]
    total_pages: int
    total_results: int


class TvPage(TypedDict, total=False):
    page: int
    results: list[TvSummary]
    total_pages: int
    total_results: int


class PersonPage(TypedDict, total=False):
    page: int
    results: list[PersonSummary]
    total_pages: int
    total_results: int


class SearchPage(TypedDict, total=False):
    """Paged results whose items vary, such as ``search.multi`` and ``trending.get``."""

    page: int
    results: list[dict[str, Any]]
    total_pages: int
    total_results: int


class FindResults(TypedDict, total=False):
    movie_results: list[MovieSummary]
    person_results: list[PersonSummary]
    tv_results: list[TvSummary]
    tv_episode_results: list[dict[str, Any]]
    tv_season_results: list[dict[str, Any]]


class ImagesConfiguration(TypedDict, total=False):
    base_url: str
    secure_base_url: str
    backdrop_sizes: list[str]
    logo_sizes: list[str]
    poster_sizes: list[str]
    profile_sizes: list[str]
    still_sizes: list[str]


class Configuration(TypedDict, total=False):
    images: ImagesConfiguration
    change_keys: list[str]


class ErrorBody(TypedDict, total=False):
    success: bool
    status_code: int
    status_message: str


class OmdbRating(TypedDict, total=False):
    Source: str
    Value: str


class OmdbItem(TypedDict, total=False):
    Title: str
    Year: str
    Rated: str
    Released: str
    Runtime: str
    Genre: str
    Director: str
    Writer: str
    Actors: str
    Plot: str
    Language: str
    Country: str
    Awards: str
    Poster: str
    Ratings: list[OmdbRating]
    Metascore: str
    imdbRating: str
    imdbVotes: str
    imdbID: str
    Type: str
    DVD: str
    BoxOffice: str
    Production: str
    Website: str
    Response: str
    Error: str


class OmdbSearchHit(TypedDict, total=False):
    Title: str
    Year: str
    imdbID: str
    Type: str
    Poster: str


class OmdbSearch(TypedDict, total=False):
    Search: list[OmdbSearchHit]
    totalResults: str
    Response: str
    Error: str


class PlanPeriod(TypedDict, total=False):
    id: str
    months: int
    save: float | int


class Plan(TypedDict, total=False):
    id: str
    name: str
    rpm: int
    monthlyCents: int
    totals: dict[str, int]


class Plans(TypedDict, total=False):
    """Result of ``plans()``. Names and prices are live, so read them at run time."""

    currency: str
    periods: list[PlanPeriod]
    plans: list[Plan]
    fetchedAt: Any
