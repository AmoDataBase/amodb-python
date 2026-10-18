"""Python client for the amodb movie and TV metadata API.

amodb is compatible with TMDB v3 and OMDb. It is a paid API: get a key at
https://amodb.dev/pricing.

    from amodb import Client

    with Client("YOUR_KEY") as client:
        movie = client.movies.details(550)
"""

from __future__ import annotations

from ._core import (
    DEFAULT_BASE_URL,
    DEFAULT_IMAGE_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_OMDB_URL,
    DEFAULT_TIMEOUT,
)
from ._endpoints import image_url
from ._version import __version__
from .async_client import AsyncClient
from .client import Client
from .errors import AmodbError, AmodbTimeoutError, NetworkError, RateLimitError

__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_IMAGE_BASE_URL",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_OMDB_URL",
    "DEFAULT_TIMEOUT",
    "AmodbError",
    "AmodbTimeoutError",
    "AsyncClient",
    "Client",
    "NetworkError",
    "RateLimitError",
    "__version__",
    "image_url",
]
