"""Provides generic parsing utilities for environment/config-sourced values."""

from collections.abc import Callable

from borgwake.errors import ConfigurationError


def parse_field[T](raw: str, parser: Callable[[str], T], field_name: str) -> T:
    """Parses a raw string value using the given parser.

    Raises:
        ConfigurationError: if parser raises ValueError.
    """

    try:
        return parser(raw)
    except ValueError as e:
        raise ConfigurationError(f"Invalid {field_name}: {raw!r}") from e
