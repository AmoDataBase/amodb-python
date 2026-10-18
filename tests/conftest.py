from __future__ import annotations

from collections.abc import Callable

import pytest

from helpers import Recorder, Reply, Runner


@pytest.fixture(params=["sync", "async"])
def flavor(request: pytest.FixtureRequest) -> str:
    """Every test that uses ``make`` runs once on Client and once on AsyncClient."""
    return str(request.param)


@pytest.fixture
def make(flavor: str) -> Callable[..., Runner]:
    def factory(*script: Reply | Exception, **options: object) -> Runner:
        return Runner(flavor, Recorder(*script), **options)

    return factory


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
