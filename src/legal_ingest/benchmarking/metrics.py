"""Strict but normalized benchmark comparison utilities."""

import re
from collections.abc import Iterable
from typing import Any


def normalize_text(value: str) -> str:
    """Normalize whitespace and case for exact metadata comparison."""

    return re.sub(r"\s+", " ", value).strip().casefold()


def normalize_value(value: Any) -> Any:
    """Normalize supported scalar/list metadata values for comparison."""

    if isinstance(value, str):
        return normalize_text(value)
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_value(item) for key, item in sorted(value.items())}
    return value


def exact_match(predicted: Any, expected: Any) -> bool:
    """Return normalized exact equality."""

    return normalize_value(predicted) == normalize_value(expected)


def safe_mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0
