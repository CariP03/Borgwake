"""Provides standard status enumerations for process outcomes."""

from enum import IntEnum


class Status(IntEnum):
    """Represents the execution outcome of a process."""

    SUCCESS = 0
    WARNING = 1
    ERROR = 2
