"""Check a parsed JSON body against a TypedDict from ``amodb.types``.

``conforms`` returns a list of problems. An empty list means the body matches: every key
is declared, every required key is present, and every value has the declared type.
It reads annotations with ``get_type_hints``, which needs Python 3.10 or newer for the
``X | None`` syntax.
"""

from __future__ import annotations

import types
import typing
from typing import Any, Literal, Union, get_args, get_origin, get_type_hints

_UNIONS: tuple[Any, ...] = (Union, getattr(types, "UnionType", Union))


def conforms(value: Any, annotation: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    _check(value, annotation, path, errors)
    return errors


def _check(value: Any, annotation: Any, path: str, errors: list[str]) -> bool:
    if annotation is Any:
        return True
    if annotation is None or annotation is type(None):
        return _expect(value is None, f"{path}: {value!r} is not None", errors)
    origin = get_origin(annotation)
    if origin in _UNIONS:
        for option in get_args(annotation):
            if _check(value, option, path, []):
                return True
        return _expect(False, f"{path}: {value!r:.60} fits none of {annotation}", errors)
    if origin is Literal:
        allowed = get_args(annotation)
        return _expect(value in allowed, f"{path}: {value!r} not in {allowed}", errors)
    if origin is list:
        if not _expect(isinstance(value, list), f"{path}: expected a list", errors):
            return False
        inner = get_args(annotation)[0]
        results = [_check(item, inner, f"{path}[{i}]", errors) for i, item in enumerate(value)]
        return all(results)
    if origin is dict:
        if not _expect(isinstance(value, dict), f"{path}: expected an object", errors):
            return False
        inner = get_args(annotation)[1]
        results = [_check(item, inner, f"{path}.{key}", errors) for key, item in value.items()]
        return all(results)
    if isinstance(annotation, type) and typing.is_typeddict(annotation):
        return _check_typed_dict(value, annotation, path, errors)
    if annotation is bool:
        good = isinstance(value, bool)
    elif annotation is int:
        good = isinstance(value, int) and not isinstance(value, bool)
    elif annotation is float:
        good = isinstance(value, (int, float)) and not isinstance(value, bool)
    elif annotation is str:
        good = isinstance(value, str)
    else:
        raise TypeError(f"unsupported annotation {annotation!r}")
    return _expect(good, f"{path}: {value!r:.60} is not {annotation.__name__}", errors)


def _check_typed_dict(value: Any, cls: Any, path: str, errors: list[str]) -> bool:
    if not _expect(isinstance(value, dict), f"{path}: expected {cls.__name__}", errors):
        return False
    hints = get_type_hints(cls)
    ok = True
    for key in value:
        if key not in hints:
            errors.append(f"{path}: key {key!r} is not declared in {cls.__name__}")
            ok = False
    for key in cls.__required_keys__:
        if key not in value:
            errors.append(f"{path}: required key {key!r} is missing from {cls.__name__}")
            ok = False
    for key, item in value.items():
        if key in hints:
            ok = _check(item, hints[key], f"{path}.{key}", errors) and ok
    return ok


def _expect(condition: bool, message: str, errors: list[str]) -> bool:
    if not condition:
        errors.append(message)
    return condition
