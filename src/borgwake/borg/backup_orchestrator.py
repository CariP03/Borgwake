"""Provides an orchestrator to cycle backup jobs."""

from borgwake.borg.abstractions import BackupExecutor, BackupJob
from borgwake.borg.borg import logger
from borgwake.status import Status


async def cycle_backups(jobs: list[BackupJob], executor: BackupExecutor) -> Status:
    """Execute all backup jobs using the given executor.

    Raises:
       BackupExecutionError: if a system or environment failure occurred.
    """

    exit_status = Status.SUCCESS
    for job in jobs:
        status = await executor.execute_backup(job)

        exit_status = max(exit_status, status)
        if status == Status.ERROR:
            logger.error(
                "An error during the execution of the backup job for repo %s has failed. "
                "Aborting remaining jobs.",
                job.repo_name,
            )

            break

    return exit_status
