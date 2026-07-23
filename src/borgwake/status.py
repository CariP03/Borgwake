"""Provides standard status enumerations for process outcomes."""

from enum import Enum


class Status(Enum):
    """Represents the execution outcome of a process."""

    SUCCESS = 0
    WARNING = 1
    ERROR = 2
