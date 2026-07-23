"""Provides abstractions for backup execution."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from borgwake.status import Status


@dataclass
class BackupJob:
    """Information about how to execute a backup."""

    repo_name: str
    repo_passphrase: str
    script_path: Path


class BackupExecutor(ABC):
    """Abstraction for backup executor."""

    @abstractmethod
    def execute_backup(self, job: BackupJob) -> Status:
        """Execute a backup using job settings."""