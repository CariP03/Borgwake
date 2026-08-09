"""Provides paths validation functionalities."""

from pathlib import Path

from borgwake.errors import ConfigurationError


def validate_path_exists(path: Path) -> Path:
    """Validates a Path by ensuring it exists.

    Raises:
        ConfigurationError: if path does not exist.
    """

    if not path.exists():
        raise ConfigurationError(f"Path {path!r} does not exist.")

    return path


def validate_path_is_a_directory(path: Path) -> Path:
    """Validates a Path by ensuring it is a directory.

    Raises:
        ConfigurationError: if path does not exist or is not a directory.
    """

    validate_path_exists(path)
    if not path.is_dir():
        raise ConfigurationError(f"Path {path!r} is not a directory.")

    return path


def validate_path_is_a_file(path: Path) -> Path:
    """Validates a Path by ensuring it is a file.

    Raises:
        ConfigurationError: if path does not exist or is not a file.
    """

    validate_path_exists(path)
    if not path.is_file():
        raise ConfigurationError(f"Path {path!r} is not a file.")

    return path
