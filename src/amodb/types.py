"""Typed dictionaries for the response objects.

Every client method returns a plain ``dict``. These classes describe the common
shapes so you can annotate your own code. The TMDB style objects are ``total=False``
because the API leaves out fields that are unknown. The amodb extension results
(``Moods``, ``Soundtracks``, ``Ratings``, ``Wikidata`` and ``Showtimes``) always send
every key, so their keys are required and a missing value is ``None``. Use
``typing.cast`` to apply one::

    from typing import cast
    from amodb.types import MovieDetails

    movie = cast(MovieDetails, client.movies.details(550))

The extension results come in two forms. The standalone call, such as
``movies.ratings(550)``, returns the ``Ratings`` form with an ``id``. The same data
inside ``append_to_response`` has no ``id`` and uses the ``RatingsSection`` form.
``Wikidata`` and ``Showtimes`` keep their ``id`` in both places.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

__all__ = [
    "Cast",
    "Configuration",
    "Credits",
    "Crew",
    "Episode",
    "ErrorBody",
    "ExternalSource",
    "FindMovie",
    "FindPerson",
    "FindResults",
    "FindTv",
    "Genre",
    "Image",
    "Images",
    "ImagesConfiguration",
    "Mood",
    "Moods",
    "MoodsSection",
    "MovieDetails",
    "MovieExternalIds",
    "MoviePage",
    "MovieSummary",
    "Network",
    "OmdbItem",
    "OmdbRating",
    "OmdbSearch",
    "OmdbSearchHit",
    "PersonDetails",
    "PersonExternalIds",
    "PersonPage",
    "PersonSummary",
    "Plan",
    "PlanPeriod",
    "Plans",
    "ProductionCompany",
    "ProductionCountry",
    "RatingValue",
    "Ratings",
    "RatingsSection",
    "SeasonDetails",
    "SeasonSummary",
    "SearchPage",
    "Showtime",
    "Showtimes",
    "ShowtimesChain",
    "ShowtimesCountry",
    "ShowtimesVenue",
    "SoundtrackAlbum",
    "SoundtrackTrack",
    "Soundtracks",
    "SoundtracksSection",
    "SpokenLanguage",
    "TvDetails",
    "TvExternalIds",
    "TvPage",
    "TvSummary",
    "Video",
    "Videos",
    "Wikidata",
    "WikidataBasedOn",
    "WikidataBoxOffice",
    "WikidataEntry",
    "WikidataLink",
    "WikidataMoney",
]

ExternalSource = Literal[
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
"""Values of ``external_source`` for ``client.find``."""


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
    adult: bool
    gender: int
    id: int
    known_for_department: str
    name: str
    original_name: str
    popularity: float
    character: str
    credit_id: str
    order: int
    profile_path: str | None


class Crew(TypedDict, total=False):
    adult: bool
    gender: int
    id: int
    known_for_department: str
    name: str
    original_name: str
    popularity: float
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


class RatingValue(TypedDict):
    """One provider score. ``votes`` is None when the provider gives no vote count."""

    value: float
    votes: int | None


class RatingsSection(TypedDict):
    """Ratings as appended with ``append_to_response=ratings``. It has no ``id``.

    A provider is None when its score is missing or 0. IMDb and Kinopoisk are out of
    10 with one decimal, TMDB is out of 10 with three decimals, and Metacritic and
    Rotten Tomatoes are out of 100.
    """

    imdb: RatingValue | None
    kinopoisk: RatingValue | None
    metacritic: RatingValue | None
    rotten_tomatoes: RatingValue | None
    tmdb: RatingValue | None


class Ratings(RatingsSection):
    """Result of ``movies.ratings`` and ``tv.ratings``."""

    id: int


class Mood(TypedDict):
    """One mood. ``avg`` and every item of ``values`` are on a 0 to 10 scale."""

    name: str
    avg: float
    values: list[float]


class MoodsSection(TypedDict):
    """Moods as appended with ``append_to_response=moods``. It has no ``id``.

    ``source`` is ``"measured"`` for viewer data, ``"estimated"`` when derived from the
    genres, and None with an empty ``results`` when the title has no data. ``results``
    is sorted by ``name``. Not every title has every mood.
    """

    source: Literal["measured", "estimated"] | None
    results: list[Mood]


class Moods(MoodsSection):
    """Result of ``movies.moods`` and ``tv.moods``."""

    id: int


class SoundtrackTrack(TypedDict):
    disc: int
    number: int
    title: str
    artist: str
    duration_ms: int


class SoundtrackAlbum(TypedDict):
    source: Literal["musicbrainz", "deezer"]
    album: str
    artist: str | None
    released: str | None
    url: str | None
    track_count: int
    tracks: list[SoundtrackTrack]


class SoundtracksSection(TypedDict):
    """Soundtracks as appended with ``append_to_response=soundtracks``. It has no ``id``.

    ``results`` is empty when no album is known. Today it holds at most one album.
    """

    results: list[SoundtrackAlbum]


class Soundtracks(SoundtracksSection):
    """Result of ``movies.soundtracks`` and ``tv.soundtracks``."""

    id: int


class _WikidataLinkRequired(TypedDict):
    wikidata_id: str
    label: str | None


class WikidataLink(_WikidataLinkRequired, total=False):
    """A Wikidata item. ``tmdb_id`` and ``media_type`` are set only for catalog titles.

    ``label`` is in the request ``language``, falling back to English.
    """

    tmdb_id: int
    media_type: Literal["movie", "tv"]


class WikidataEntry(WikidataLink, total=False):
    """A link with an optional ``year``, used by ``awards`` and ``nominations``."""

    year: int


class WikidataBasedOn(WikidataEntry):
    """A source work. ``author`` is None when it is not known."""

    author: WikidataLink | None


class WikidataMoney(TypedDict):
    """An amount rounded to an integer. ``currency`` is an ISO code or None."""

    value: int
    currency: str | None


class WikidataBoxOffice(WikidataMoney):
    worldwide: bool


class Wikidata(TypedDict):
    """Result of ``movies.wikidata`` and ``tv.wikidata``. It keeps its ``id`` when appended.

    ``sitelinks`` maps a language code to a Wikipedia page title. Empty groups are
    empty lists.
    """

    id: int
    wikidata_id: str | None
    budget: WikidataMoney | None
    box_office: WikidataBoxOffice | None
    follows: WikidataLink | None
    followed_by: WikidataLink | None
    sitelinks: dict[str, str]
    awards: list[WikidataEntry]
    nominations: list[WikidataEntry]
    based_on: list[WikidataBasedOn]
    filming_locations: list[WikidataLink]
    narrative_locations: list[WikidataLink]
    original_broadcasters: list[WikidataLink]


class ShowtimesCountry(TypedDict):
    """Per country counts. ``first_day`` and ``last_day`` are ``YYYY-MM-DD`` dates."""

    country: str
    name: str
    venues: int
    cities: int
    showtimes: int
    first_day: str
    last_day: str


class ShowtimesChain(TypedDict):
    key: str
    name: str | None


class Showtime(TypedDict):
    """One screening. ``start`` is ``YYYY-MM-DDTHH:MM`` in the venue's local time."""

    date: str
    start: str
    end: str | None
    auditorium: str | None
    formats: list[str]
    tags: list[str]
    audio: str | None
    subtitles: str | None
    language: str | None
    price: float | None
    currency: str | None
    prices: Any
    booking_url: str | None
    sold_out: bool


class ShowtimesVenue(TypedDict):
    id: int
    name: str
    chain: ShowtimesChain
    city: str | None
    region: str | None
    address: str | None
    postal_code: str | None
    country: str
    timezone: str | None
    latitude: float | None
    longitude: float | None
    phone: str | None
    url: str | None
    showtimes: list[Showtime]


class Showtimes(TypedDict):
    """Result of ``movies.showtimes`` and ``tv.showtimes``.

    Without a country, ``country`` is None, ``results`` is empty and ``countries`` has
    one count row per country. With a country, ``results`` lists the venues, each with
    its ``showtimes`` from today on.
    """

    id: int
    country: str | None
    results: list[ShowtimesVenue]
    countries: list[ShowtimesCountry]


class MovieExternalIds(TypedDict, total=False):
    """``id`` is missing when appended. ``kinopoisk_id`` is missing when not known."""

    id: int
    imdb_id: str | None
    wikidata_id: str | None
    facebook_id: str | None
    instagram_id: str | None
    twitter_id: str | None
    kinopoisk_id: str


class TvExternalIds(TypedDict, total=False):
    """``id`` is missing when appended. ``kinopoisk_id`` is missing when not known."""

    id: int
    imdb_id: str | None
    freebase_mid: str | None
    freebase_id: str | None
    tvdb_id: int | None
    tvrage_id: int | None
    wikidata_id: str | None
    facebook_id: str | None
    instagram_id: str | None
    twitter_id: str | None
    kinopoisk_id: str


class PersonExternalIds(TypedDict, total=False):
    """``id`` is missing when appended."""

    id: int
    imdb_id: str | None
    wikidata_id: str | None
    facebook_id: str | None
    instagram_id: str | None
    tiktok_id: str | None
    twitter_id: str | None
    youtube_id: str | None


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
    origin_country: list[str]
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
    # Present only when requested with append_to_response. Other names that work there,
    # such as watch/providers, are not typed here.
    credits: Credits
    images: Images
    videos: Videos
    external_ids: MovieExternalIds
    ratings: RatingsSection
    moods: MoodsSection
    soundtracks: SoundtracksSection
    wikidata: Wikidata
    showtimes: Showtimes


class TvSummary(TypedDict, total=False):
    adult: bool
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
    vote_average: float


class Network(TypedDict, total=False):
    id: int
    logo_path: str | None
    name: str
    origin_country: str


class TvDetails(TypedDict, total=False):
    adult: bool
    backdrop_path: str | None
    created_by: list[dict[str, Any]]  # empty for most shows
    episode_run_time: list[int]
    first_air_date: str
    genres: list[Genre]
    homepage: str
    id: int
    in_production: bool
    languages: list[str]
    last_air_date: str | None
    last_episode_to_air: dict[str, Any] | None
    name: str
    next_episode_to_air: dict[str, Any] | None
    networks: list[Network]
    number_of_episodes: int
    number_of_seasons: int
    origin_country: list[str]
    original_language: str
    original_name: str
    overview: str
    popularity: float
    poster_path: str | None
    production_companies: list[ProductionCompany]
    production_countries: list[ProductionCountry]
    seasons: list[SeasonSummary]
    spoken_languages: list[SpokenLanguage]
    status: str
    tagline: str
    vote_average: float
    vote_count: int
    # Present only when requested with append_to_response. Other names that work there,
    # such as watch/providers, are not typed here.
    credits: Credits
    images: Images
    videos: Videos
    external_ids: TvExternalIds
    ratings: RatingsSection
    moods: MoodsSection
    soundtracks: SoundtracksSection
    wikidata: Wikidata
    showtimes: Showtimes


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
    known_for: list[dict[str, Any]]  # empty in find results


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
    id: int  # only on keywords.movies
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


class FindMovie(MovieSummary):
    media_type: Literal["movie"]


class FindTv(TvSummary):
    media_type: Literal["tv"]


class FindPerson(PersonSummary):
    media_type: Literal["person"]


class FindResults(TypedDict):
    """Result of ``client.find``. The episode and season lists are always empty."""

    movie_results: list[FindMovie]
    person_results: list[FindPerson]
    tv_results: list[FindTv]
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
