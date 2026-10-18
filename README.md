<p align="center">
  <a href="https://amodb.dev">
    <img src="https://raw.githubusercontent.com/amodb-dev/.github/main/assets/lockup.png" alt="amodb" width="260">
  </a>
</p>

<h1 align="center">amodb-python</h1>

<p align="center">Python client for the amodb movie and TV metadata API. Sync, async and typed.</p>

<p align="center">
  <a href="https://github.com/amodb-dev/amodb-python/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/amodb-dev/amodb-python/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://pypi.org/project/amodb/"><img alt="PyPI version" src="https://img.shields.io/pypi/v/amodb"></a>
  <a href="https://github.com/amodb-dev/amodb-python/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/amodb-dev/amodb-python"></a>
</p>

Typed Python client for the amodb movie and TV metadata API. It covers the TMDB v3 read endpoints, the OMDb compatible endpoint and the amodb extras (ratings, moods, soundtracks, wikidata, showtimes). Account, authentication and list write endpoints are not offered. It ships a sync `Client` and an async `AsyncClient`, both built on httpx.

amodb is a paid API. Get a key at https://amodb.dev/pricing. There is no free tier and no trial.

Existing TMDB clients work by changing the base URL to `https://api.amodb.dev/3`.

## Install

```sh
pip install amodb
```

Python 3.9 or newer. The only dependency is httpx.

## Quick start

```python
import os
from amodb import Client

with Client(os.environ["AMODB_API_KEY"]) as client:
    movie = client.movies.details(550)
    print(movie["title"], movie["release_date"])

    for item in client.search.movie("inception")["results"][:3]:
        print(item["id"], item["title"])
```

Keep the key in an environment variable. The client raises `ValueError` when the key is empty.

## Async quick start

```python
import asyncio
import os
from amodb import AsyncClient


async def main() -> None:
    async with AsyncClient(os.environ["AMODB_API_KEY"]) as client:
        movie, show = await asyncio.gather(
            client.movies.details(550),
            client.tv.details(1399),
        )
        print(movie["title"], show["name"])


asyncio.run(main())
```

`AsyncClient` has the same methods and arguments as `Client`. Every method returns a coroutine.

## Search and lists

```python
client.search.movie("inception", year=2010, page=2)
client.search.tv("severance")
client.search.multi("alien")
client.search.collection("matrix")
client.movies.popular(page=2, region="US")
client.movies.latest()
client.trending.get("movie", "week")
client.tv.season(1399, 1)
client.tv.episode(1399, 1, 2)
client.discover.movie(sort_by="popularity.desc", with_genres=[28, 12])
client.discover.movie({"release_date.gte": "2020-01-01"})
```

Lists take `page` from 1 to 500. Any extra keyword becomes a query parameter. Lists are joined with commas, booleans become `true` and `false`, and `None` values are dropped. For names that are not valid Python identifiers, pass a dict, as in the last line above. Every method also accepts `params={...}`.

## Details with append_to_response

```python
movie = client.movies.details(550, append_to_response=["credits", "images", "ratings"])
print(movie["credits"]["cast"][0]["name"])
```

Pass up to 20 names. Names the API does not know are ignored without an error. For movies and TV shows these work: `credits`, `images`, `videos`, `keywords`, `translations`, `external_ids`, `similar`, `recommendations`, `reviews`, `watch/providers`, `alternative_titles`, `lists`, `moods`, `soundtracks`, `ratings`, `wikidata` and `showtimes`, plus `release_dates` for movies and `content_ratings` and `episode_groups` for TV. People take `combined_credits`, `movie_credits`, `tv_credits`, `external_ids` and `images`.

## Language

```python
client = Client(key, language="ru-RU")  # default for every call
client.movies.details(550)  # sends language=ru-RU
client.movies.details(550, language="pt-BR")  # a per call value wins
```

amodb serves 14 base languages: en, ru, uk, be, zh, pt, bg, he, cs, ro, fr, pl, it and es. Any other tag falls back to `en`.

## Images

```python
movie = client.movies.details(550)
client.image_url(movie["poster_path"], "w500")  # https://img.amodb.dev/t/p/w500/...

from amodb import image_url

image_url("/abc.jpg", "original")
```

Sizes are `w92`, `w154`, `w185`, `w300`, `w342`, `w500`, `w780`, `w1280`, `h632` and `original`. An empty path returns `None`. Image URLs need no key.

## OMDb

```python
client.omdb.by_id("tt0137523", plot="full")
client.omdb.by_title("Fight Club", year=1999, type="movie")
client.omdb.search("fight", type="movie", page=2)
```

OMDb calls send the key as the `apikey` query parameter. When the answer is HTTP 200 with `"Response": "False"`, the client raises `AmodbError` with `status` 200 and the `Error` text as `status_message`.

## Find by external id

```python
found = client.find("tt0137523", "imdb_id")
print(found["movie_results"][0]["title"])  # Fight Club

client.find("361", "kinopoisk_id")
client.find("Q190050", "wikidata_id")
```

`external_source` is one of `imdb_id`, `freebase_mid`, `freebase_id`, `tvdb_id`, `tvrage_id`, `facebook_id`, `twitter_id`, `instagram_id`, `tiktok_id`, `youtube_id`, `wikidata_id` and `kinopoisk_id`. IMDb, TVDB, Facebook, Twitter, Instagram, Wikidata and Kinopoisk ids resolve. The others are accepted and return empty lists. The reply has `movie_results`, `person_results`, `tv_results`, `tv_episode_results` and `tv_season_results`. Each item has a `media_type`, and the episode and season lists are always empty. A missing or unknown source answers 400 with code 22.

## amodb extras

Every extra works on movies and on TV shows, for example `client.movies.ratings(550)` and `client.tv.ratings(1399)`.

```python
ratings = client.movies.ratings(550)
print(ratings["imdb"])  # {"value": 8.8, "votes": 2669989}
print(ratings["metacritic"]["value"])  # 67, out of 100
```

A provider is `{"value": ..., "votes": ...}` or `None` when it has no score. `votes` can be `None`. IMDb, Kinopoisk and TMDB are out of 10, and Metacritic and Rotten Tomatoes are out of 100.

```python
moods = client.movies.moods(155)
print(moods["source"])  # "measured"
for mood in moods["results"]:
    print(mood["name"], mood["avg"])  # action 3.9
```

`source` is `"measured"` for viewer data, `"estimated"` when derived from the genres, or `None` with an empty `results` for a title without data. `avg` and every item of `values` use a 0 to 10 scale.

```python
album = client.movies.soundtracks(155)["results"][0]
print(album["album"], album["artist"], album["track_count"])
print(album["tracks"][0]["title"], album["tracks"][0]["duration_ms"])  # Why So Serious? 554000
```

`results` is empty when no album is known. An album has a `source` (`"musicbrainz"` or `"deezer"`) and a `tracks` list.

```python
facts = client.movies.wikidata(550)
print(facts["budget"])  # {"value": 63000000, "currency": "USD"}
print(facts["box_office"]["worldwide"])  # True
print(facts["sitelinks"]["en"])  # Fight Club
```

Money fields are `{"value", "currency"}` or `None`. The reply also has `awards`, `nominations`, `based_on`, `follows`, `followed_by`, `filming_locations`, `narrative_locations` and `original_broadcasters`. Items are `{"wikidata_id", "label"}` and carry `tmdb_id` and `media_type` when the item is a title in the catalog.

```python
summary = client.movies.showtimes(550)  # no country: counts per country
for row in summary["countries"]:
    print(row["country"], row["venues"], row["showtimes"], row["first_day"], row["last_day"])

for venue in client.movies.showtimes(550, "RU")["results"]:
    for show in venue["showtimes"]:
        print(venue["name"], show["start"], show["booking_url"])
```

`country` is optional. Without it, `results` is empty and `country` is `None`, and `countries` lists up to 60 countries that have showtimes from today on. With a two letter country, `results` lists venues, each with its `showtimes`. `start` is in the venue's local time. `region="RU"` works in place of `country`. To append showtimes, pass `country` as well:

```python
client.movies.details(550, append_to_response=["moods", "ratings", "showtimes"], country="RU")
```

An appended `moods`, `ratings` or `soundtracks` section has no `id`. `wikidata` and `showtimes` keep theirs.

## Paths that are not offered

These TMDB paths answer 404 with code 34, so the client has no method for them: `aggregate_credits`, `changes`, `credit/{id}`, `review/{id}`, `person/{id}/translations`, `person/{id}/tagged_images`, `tv/episode_group/{id}`, `tv/{id}/screened_theatrically`, `configuration/timezones`, and `images`, `translations` and `alternative_names` for collections, companies and networks. Anything under `account`, `authentication`, `guest_session` and `list` answers 405 with code 37. `reviews` is always empty, and `include_adult` is ignored because adult titles are never served.

## Plans and rate limits

Every plan gets all data. Plans differ only in requests per minute: `lite` 20, `pro` 40 and `proplus` 120. Prices are live, so read them at run time. The call sends no key.

```python
for plan in client.plans()["plans"]:
    print(plan["id"], plan["name"], plan["rpm"])
```

The full list is at https://api.amodb.dev/plans. Every keyed response carries `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers.

## Errors

```python
from amodb import AmodbError, AmodbTimeoutError, NetworkError, RateLimitError

try:
    client.movies.details(550)
except RateLimitError as err:
    print("over the limit, retry after", err.retry_after)
except AmodbTimeoutError:
    print("timed out")
except NetworkError:
    print("could not connect")
except AmodbError as err:
    print(err.status, err.status_code, err.status_message, err.body)
```

| Class | When |
|---|---|
| `AmodbError` | Base class. An HTTP error, an OMDb `"Response": "False"` answer, or a body that is not JSON. |
| `RateLimitError` | HTTP 429 after the retries are used up. Adds `retry_after` in seconds, or `None`. |
| `AmodbTimeoutError` | The request timed out. `status` is 0. |
| `NetworkError` | DNS, connection or TLS failure. `status` is 0. |

Every error has `status` (HTTP status), `status_code` (the number from the error body, or `None`), `status_message` and `body` (parsed JSON, raw text, or `None`).

Common answers: 401 with code 7 for an invalid key, 402 with code 36 for an expired plan, 404 with code 34 for a missing resource, 405 with code 37 for account, authentication, list and rating paths, which amodb does not offer.

## Retries and timeouts

- Only HTTP 429 is retried. Other failures are raised at once.
- The wait is the `Retry-After` header (seconds or an HTTP date), limited to 0 to 60 seconds. Without the header the waits are 1, 2 and 4 seconds.
- `max_retries` defaults to 3 and is capped at 3, so a call makes at most 4 attempts. After that you get `RateLimitError`.
- `timeout` defaults to 15 seconds. Pass a number or an `httpx.Timeout`.

```python
client = Client(key, timeout=30, max_retries=1)
```

Pass `sleep=` to replace the wait function. Tests use it to run instantly.

## Custom httpx client

```python
import httpx
from amodb import Client

http = httpx.Client(timeout=30, limits=httpx.Limits(max_connections=10))
client = Client(key, http_client=http)  # you close http yourself

client = Client(key, transport=httpx.HTTPTransport(retries=2))
```

For tests, use `httpx.MockTransport` and no network is needed:

```python
def handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"id": 550, "title": "Test"})


client = Client("test-key", transport=httpx.MockTransport(handler))
```

`AsyncClient` takes `httpx.AsyncClient` and `httpx.AsyncBaseTransport` in the same places.

## Options

| Option | Default | Notes |
|---|---|---|
| `api_key` | required | Your amodb key. |
| `base_url` | `https://api.amodb.dev/3` | TMDB style base URL. |
| `omdb_url` | `https://api.amodb.dev/omdb/` | OMDb style URL. |
| `image_base_url` | `https://img.amodb.dev/t/p/` | Used by `image_url`. |
| `language` | none | Default `language` for TMDB style calls. |
| `timeout` | 15 | Seconds, or an `httpx.Timeout`. |
| `max_retries` | 3 | Retries on HTTP 429. Never more than 3. |
| `auth` | `"bearer"` | `"bearer"` sends `Authorization: Bearer KEY`. `"query"` sends `api_key=KEY` in the URL. |
| `http_client` | none | Your own `httpx.Client` or `httpx.AsyncClient`. |
| `transport` | none | A custom httpx transport. |
| `sleep` | `time.sleep` or `asyncio.sleep` | Wait function for retries. |

Prefer the default `bearer` mode. It keeps the key out of URLs and logs.

## Raw requests

```python
client.request("/movie/550", {"language": "ru-RU"})
```

`request` uses the same auth, retries and error handling and returns the parsed JSON.

## Typed responses

Methods return plain dicts. The `amodb.types` module has `TypedDict` classes for the main shapes. Use `cast` to apply one:

```python
from typing import cast
from amodb.types import MovieDetails, Moods, Showtimes

movie = cast(MovieDetails, client.movies.details(550))
moods = cast(Moods, client.movies.moods(155))
showtimes = cast(Showtimes, client.movies.showtimes(550, "RU"))
```

The extension types `Moods`, `Soundtracks`, `Ratings`, `Wikidata` and `Showtimes` list every key the API always sends, so those keys are required. `MoodsSection`, `SoundtracksSection` and `RatingsSection` describe the same data inside `append_to_response`, where there is no `id`.

The package ships a `py.typed` marker.

## Development

```sh
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
ruff check .
mypy
python -m build
```

Tests use `httpx.MockTransport` and never touch the network.

## Links

- Website: https://amodb.dev
- Docs: https://amodb.dev/docs
- Pricing: https://amodb.dev/pricing
- Status: https://amodb.dev/status
- Issues: https://github.com/amodb-dev/amodb-python/issues
- Changelog: https://github.com/amodb-dev/amodb-python/blob/main/CHANGELOG.md
- Security: https://github.com/amodb-dev/amodb-python/blob/main/SECURITY.md
- Organization: https://github.com/amodb-dev

## License

MIT. See `LICENSE`.
