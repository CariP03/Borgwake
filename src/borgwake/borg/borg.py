"""Provides functionalities to execute backups using BorgBackup."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import override

from borgwake.borg.abstractions import BackupExecutor, BackupJob
from borgwake.status import Status


@dataclass
class BorgBackupSettings:
    """Global settings to execute backups using BorgBackup."""

    host: str
    username: str
    repo_base_path: Path
    script_base_path: Path

def load_borg_backup_settings(host: str) -> BorgBackupSettings | None:
    """Load Borg backup global settings from the environment.

    Returns None if any of the settings is not set.

    Raises:
        EnvConfigurationError: if an env variable is set but invalid.
    """

    username = os.getenv("BACKUP_USERNAME")
    repo_base_path = Path(os.getenv("BACKUP_BASE_PATH"))
    script_base_path = Path(os.getenv("BACKUP_SCRIPTS_BASE_PATH"))

    if username is None or repo_base_path is None or script_base_path is None:
        return None

    return BorgBackupSettings(
        host=host,
        username=username,
        repo_base_path=repo_base_path,
        script_base_path=script_base_path)

class BorgBackupExecutor(BackupExecutor):
    """Executor for backups using BorgBackup."""

    def __init__(self, settings: BorgBackupSettings):
        self._settings = settings

    @override
    def execute_backup(self, job: BackupJob) -> Status:
