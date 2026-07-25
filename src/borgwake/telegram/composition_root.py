"""Provides functionalities to construct the dependency graph."""

from collections.abc import Coroutine

from borgwake.backup.borg import BorgBackupExecutor
from borgwake.kasa.kasa_locator import KasaLocator
from borgwake.kasa.kasa_plug import KasaPlug
from borgwake.networking.reachability_checker import ReachabilityChecker
from borgwake.power.remote_host_power_controller import RemoteHostPowerController
from borgwake.power.sequential_shutdown import SequentialShutdown
from borgwake.power.ssh_shutdown import SSHShutdown
from borgwake.telegram.telegram_bot import TelegramNotifier
from borgwake.workflow import run_workflow


async def compose() -> Coroutine:
    host = await resolve_host()

    kasa_locator = KasaLocator()
    plug = KasaPlug()

    ssh_shutdown = SSHShutdown()

    sequential_shutdown = SequentialShutdown()
    power_controller = RemoteHostPowerController(plug, sequential_shutdown)

    reachability_checker = ReachabilityChecker(host)

    jobs =

    backup_executor = BorgBackupExecutor()

    notifier = TelegramNotifier()

    return run_workflow(
        power_controller,
        reachability_checker,
        jobs,
        backup_executor,
        notifier
    )


async def resolve_host() -> str:
    pass
