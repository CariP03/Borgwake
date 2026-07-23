"""Provides generic YAML file reading."""

from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> Any:
    """Read and parse a YAML file into Python data structures."""

    with path.open("r") as f:
        return yaml.safe_load(f)
