"""Provides an orchestrator to cycle backup jobs."""

from borgwake.backup.abstractions import BackupExecutor, BackupJob, BackupStatus
from borgwake.backup.borg import logger


async def cycle_backups(
    jobs: list[BackupJob], executor: BackupExecutor
) -> BackupStatus:
    """Execute all backup jobs using the given executor.

    Raises:
       BackupExecutionError: if a system or environment failure occurred.
    """

    exit_status = BackupStatus.SUCCESS
    for job in jobs:
        status = await executor.execute_backup(job)

        exit_status = max(exit_status, status)
        if status == BackupStatus.ERROR:
            logger.error(
                "An error during the execution of the backup job for repo %s has failed. "
                "Aborting remaining jobs.",
                job.repo_name,
            )

            break

    return exit_status
