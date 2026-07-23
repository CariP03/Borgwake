"""Provides abstractions for backup execution."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from borgwake.status import Status

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
    async def execute_backup(self, job: BackupJob) -> Status:
        """Execute a backup using job settings.

        Raises:
            BackupExecutionError: if a system or environment failure occurred.
        """
