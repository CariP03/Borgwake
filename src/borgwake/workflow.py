"""Provides the orchestrator logic to run the whole workflow."""

from borgwake.borg.abstractions import BackupExecutor, BackupJob
from borgwake.borg.backup_orchestrator import cycle_backups
from borgwake.networking.reachability_checker import ReachabilityChecker
from borgwake.notifier.notifier import Notifier
from borgwake.power.remote_host_power_controller import RemoteHostPowerController
from borgwake.status import Status


async def run_workflow(
    power_controller: RemoteHostPowerController,
    reachability_checker: ReachabilityChecker,
    jobs: list[BackupJob],
    executor: BackupExecutor,
    notifier: Notifier,
) -> Status:
    status = Status.SUCCESS

    was_host_online = await reachability_checker.is_online()
    if not was_host_online:
        await power_controller.turn_on()

        if not await reachability_checker.wait_until_online():
            status = Status.ERROR

    if status != Status.ERROR:
        status = await cycle_backups(jobs, executor)

    if not was_host_online:
        await power_controller.turn_off()

    await notifier.notify(status)
    return status
