"""Provides functionalities to execute backups using BorgBackup."""

import asyncio
import os
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import override

from borgwake.borg.abstractions import BackupExecutionError, BackupExecutor, BackupJob
from borgwake.status import Status

logger = getLogger(__name__)


BORG_SUCCESS_RETURN_CODE = 0
BORG_WARNING_RETURN_CODE = 1


@dataclass
class BorgBackupSettings:
    """Global settings to execute backups using BorgBackup."""

    host: str
    username: str
    repo_base_path: Path


def load_borg_backup_settings(host: str) -> BorgBackupSettings | None:
    """Load Borg backup global settings from the environment.

    Returns None if any of the settings is not set.
    """

    username = os.getenv("BACKUP_USERNAME")
    repo_base_path_raw = os.getenv("BACKUP_BASE_PATH")

    if username is None or repo_base_path_raw is None:
        return None

    return BorgBackupSettings(
        host=host, username=username, repo_base_path=Path(repo_base_path_raw)
    )


class BorgBackupExecutor(BackupExecutor):
    """Executor for backups using BorgBackup."""

    def __init__(self, settings: BorgBackupSettings):
        self._settings = settings

    @override
    async def execute_backup(self, job: BackupJob) -> Status:
        try:
            borg_repo = f"ssh://{self._settings.username}@{self._settings.host}{self._settings.repo_base_path}/{job.repo_name}"

            logger.info("Executing backup script %s", job.script_path)

            env = {
                "PATH": os.environ["PATH"],
                "HOME": os.environ["HOME"],
                "BORG_REPO": borg_repo,
                "BORG_PASSPHRASE": job.repo_passphrase,
            }

            process = await asyncio.create_subprocess_exec(
                str(job.script_path),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            output, _ = await process.communicate()
            logger.debug("Backup script %s output: %s", job.script_path, output.decode())

            return_code = process.returncode

            if return_code == BORG_SUCCESS_RETURN_CODE:
                logger.info("Backup succeeded")
                return Status.SUCCESS
            elif return_code == BORG_WARNING_RETURN_CODE:
                logger.warning("Backup completed with warnings")
                return Status.WARNING
            else:
                logger.error("Backup failed")
                return Status.ERROR

        except (OSError, KeyError) as e:
            raise BackupExecutionError(
                "A system or environment failure occurred "
                "and the backup has not been executed"
            ) from e
