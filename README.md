<!-- GitHub topics: amodb, tmdb, omdb, python, movie-api, tv-api, api-client, sdk, httpx, asyncio -->

# amodb for Python

Typed Python client for the amodb movie and TV metadata API. It covers the TMDB v3 read endpoints, the OMDb compatible endpoint and the amodb extras (ratings, moods, soundtracks, showtimes). It ships a sync `Client` and an async `AsyncClient`, both built on httpx.

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
client.movies.popular(page=2, region="US")
client.trending.get("movie", "week")
client.tv.season(1399, 1)
client.tv.episode(1399, 1, 2)
client.discover.movie(sort_by="popularity.desc", with_genres=[28, 12])
client.discover.movie({"release_date.gte": "2020-01-01"})
```

Any extra keyword becomes a query parameter. Lists are joined with commas, booleans become `true` and `false`, and `None` values are dropped. For names that are not valid Python identifiers, pass a dict, as in the last line above. Every method also accepts `params={...}`.

## Details with append_to_response

```python
movie = client.movies.details(550, append_to_response=["credits", "images", "ratings"])
print(movie["credits"]["cast"][0]["name"])
```

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
client.find("tt0137523", "imdb_id")
```

## amodb extras

```python
ratings = client.movies.ratings(550)
print(ratings["imdb"])  # {"value": ..., "votes": ...} or None

client.movies.moods(550)
client.tv.soundtracks(1399)
client.movies.wikidata(550)
client.movies.showtimes(550, "US")

client.movies.details(550, append_to_response=["ratings", "moods", "soundtracks"])
```

Each rating is a dict with `value` and `votes`, or `None` when the source has no score.

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

Common answers: 401 with code 7 for an invalid key, 402 with code 36 for an expired plan, 404 with code 34 for a missing resource, 405 with code 37 for TMDB write methods, which amodb does not offer.

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
from amodb.types import MovieDetails

movie = cast(MovieDetails, client.movies.details(550))
```

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

## License

MIT. See `LICENSE`.
