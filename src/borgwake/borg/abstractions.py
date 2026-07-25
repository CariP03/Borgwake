"""Provides abstractions for backup execution."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum


class BackupStatus(IntEnum):
    """Represents the execution outcome of the backup process."""

    SUCCESS = 0
    WARNING = 1
    ERROR = 2


class BackupExecutionError(Exception):
    """A system or environment failure prevented the backup from executing."""


@dataclass
class BackupJob:
    """Information about how to execute a backup."""

    repo_name: str
    repo_passphrase: str
    script_path: str


class BackupExecutor(ABC):
    """Abstraction for backup executor."""

    @abstractmethod
    async def execute_backup(self, job: BackupJob) -> BackupStatus:
        """Execute a backup using job settings.

        Raises:
            BackupExecutionError: if a system or environment failure occurred.
        """
