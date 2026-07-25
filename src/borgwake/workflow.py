"""Provides the orchestrator logic to run the whole workflow."""

import logging

from borgwake.backup.abstractions import (
    BackupExecutionError,
    BackupExecutor,
    BackupJob,
    BackupStatus,
)
from borgwake.backup.backup_orchestrator import cycle_backups
from borgwake.networking.reachability_checker import (
    ReachabilityChecker,
    ReachabilityCheckError,
)
from borgwake.notifier.notifier import Notifier, NotifierError
from borgwake.power.abstractions import ShutdownFailure, TurnOnFailure
from borgwake.power.remote_host_power_controller import RemoteHostPowerController

logger = logging.getLogger(__name__)


async def run_workflow(
    power_controller: RemoteHostPowerController,
    reachability_checker: ReachabilityChecker,
    jobs: list[BackupJob],
    executor: BackupExecutor,
    notifier: Notifier,
) -> BackupStatus:
    """Run the whole Borgwake workflow.

    Raises:
        ShutdownFailure: if an error has occurred while turning off the remote host.
        NotifierError: if an error has occurred while notifying.
    """

    status = BackupStatus.SUCCESS
    was_host_online = True

    try:
        was_host_online = await reachability_checker.is_online()
        if not was_host_online:
            await power_controller.turn_on()

            if not await reachability_checker.wait_until_online():
                status = BackupStatus.ERROR
                return status

        status = await cycle_backups(jobs, executor)
        return status

    except ReachabilityCheckError as e:
        logger.error(
            "An error has occurred while trying to check the status of the remote host. Error: %s",
            e,
        )

        status = BackupStatus.ERROR
        return status
    except TurnOnFailure as e:
        logger.error(
            "An error has occurred while trying to turn on the remote host. Error: %s",
            e,
        )

        status = BackupStatus.ERROR
        return status
    except BackupExecutionError as e:
        logger.error(
            "An error has occurred while trying to execute the backup. Error: %s", e
        )
        status = BackupStatus.ERROR

        return status

    finally:
        shutdown_error: ShutdownFailure | None = None
        try:
            if not was_host_online:
                await power_controller.turn_off()
        except ShutdownFailure as e:
            logger.error(
                "An error has occurred while trying to shutdown the remote host. Error: %s",
                e,
            )

            shutdown_error = e
            if status != BackupStatus.ERROR:
                status = BackupStatus.WARNING

        try:
            await notifier.notify(status)
        except NotifierError as e:
            logger.error(
                "An error has occurred while trying to notify the notifier. Error: %s",
                e,
            )
            raise
        if shutdown_error is not None:
            raise shutdown_error
