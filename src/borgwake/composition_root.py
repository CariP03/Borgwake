"""Constructs the application's dependency graph.

This is the only module allowed to know about every concrete implementation at
once. Everything below it depends on abstractions; everything above it (the
entry point) depends only on `compose`.
"""

import logging

from kasa import Device, Discover, KasaException

from borgwake.backup.abstractions import BackupExecutor, BackupStatus
from borgwake.backup.borg import BorgBackupExecutor, load_borg_backup_settings
from borgwake.backup.job_parser import (
    load_backup_jobs,
    load_backup_jobs_loading_settings,
    parse_backup_jobs,
)
from borgwake.errors import ConfigurationError, HostResolutionError
from borgwake.kasa.kasa_loader import KasaSettings, load_kasa_settings
from borgwake.kasa.kasa_locator import KasaLocator
from borgwake.kasa.kasa_plug import KasaPlug
from borgwake.networking.arp_locator import ArpLocator, load_arp_settings
from borgwake.networking.device_locator import DeviceLocator
from borgwake.networking.reachability_checker import ReachabilityChecker
from borgwake.networking.static_ip_locator import StaticIpLocator, load_static_host_ip
from borgwake.notifier.notifier import Notifier
from borgwake.power.abstractions import TurnableOff
from borgwake.power.remote_host_power_controller import RemoteHostPowerController
from borgwake.power.sequential_shutdown import SequentialShutdown
from borgwake.power.ssh_shutdown import SSHShutdown, load_ssh_shutdown_settings
from borgwake.telegram.telegram_bot import TelegramNotifier, load_telegram_bot_settings
from borgwake.workflow import run_workflow

logger = logging.getLogger(__name__)


async def compose() -> BackupStatus:
    """Build the object graph, run the workflow, and return its outcome.

    Owns the full lifecycle of the plug's connection: the connection is
    opened before the workflow runs and is always closed afterwards, even if
    the workflow raises.

    Raises:
        ConfigurationError: if a required component is missing from the environment.
        HostResolutionError: if the remote host or the plug cannot be located.
    """

    host = await _resolve_host()
    reachability_checker = ReachabilityChecker(host)

    kasa_settings = _require(load_kasa_settings(), "Kasa plug")
    device = await _connect_plug(kasa_settings)

    async with KasaPlug(device, kasa_settings.power_cycle_delay) as plug:
        power_controller = RemoteHostPowerController(
            activator=plug,
            sleeper=_build_shutdown(plug, host, reachability_checker),
        )

        jobs_loading_settings = _require(
            load_backup_jobs_loading_settings(), "Backup jobs settings"
        )
        jobs = parse_backup_jobs(
            load_backup_jobs(jobs_loading_settings.jobs_file),
            jobs_loading_settings.scripts_dir,
        )
        executor = _build_backup_executor(host)
        notifier = _build_notifier()

        return await run_workflow(
            power_controller,
            reachability_checker,
            jobs,
            executor,
            notifier,
        )


async def _resolve_host() -> str:
    """Determine the remote host's IP address.

    Prefers a statically configured IP and falls back to an ARP scan.

    Raises:
        ConfigurationError: if neither addressing strategy is configured.
        HostResolutionError: if the configured locator cannot find the host.
    """

    locator = _build_host_locator()

    address = await locator.locate_device()
    if address is None:
        raise HostResolutionError(
            "The remote host could not be located on the network."
        )

    return address.ip


def _build_host_locator() -> DeviceLocator:
    """Select the addressing strategy for the remote host."""

    static_ip = load_static_host_ip()
    if static_ip is not None:
        logger.debug("Locating the remote host by static IP.")
        return StaticIpLocator(static_ip)

    arp_settings = load_arp_settings()
    if arp_settings is not None:
        logger.debug("Locating the remote host by ARP scan.")
        return ArpLocator(arp_settings)

    raise ConfigurationError(
        "No way to address the remote host: set either HOST_STATIC_IP or "
        "REMOTE_HOST_MAC."
    )


async def _connect_plug(settings: KasaSettings) -> Device:
    """Locate the Kasa plug on the network and open a connection to it.

    Raises:
        HostResolutionError: if the plug cannot be located or connected to.
    """

    address = await KasaLocator(settings).locate_device()
    if address is None:
        raise HostResolutionError(
            f"No Kasa plug with MAC {settings.plug_mac} was found on the network."
        )

    try:
        device = await Discover.discover_single(
            address.ip, credentials=settings.credentials
        )
    except KasaException as e:
        raise HostResolutionError(
            f"Failed to connect to the Kasa plug at {address.ip}."
        ) from e

    if device is None:
        raise HostResolutionError(
            f"The Kasa plug at {address.ip} did not respond to a direct connection."
        )

    return device


def _build_shutdown(
    plug: TurnableOff, host: str, reachability_checker: ReachabilityChecker
) -> TurnableOff:
    """Assemble the shutdown strategy.

    When SSH is configured the host is asked to shut down gracefully before its
    power is cut; otherwise the plug is the only stage.
    """

    ssh_settings = load_ssh_shutdown_settings()
    if ssh_settings is None:
        logger.warning(
            "SSH_USERNAME is not set: the remote host will be powered off without a "
            "graceful shutdown."
        )
        return plug

    ssh_shutdown = SSHShutdown(ssh_settings, host, reachability_checker)
    return SequentialShutdown(first=ssh_shutdown, second=plug)


def _build_backup_executor(host: str) -> BackupExecutor:
    """Assemble the backup executor.

    Raises:
        ConfigurationError: if Borg is not configured.
    """

    settings = _require(load_borg_backup_settings(host), "Borg backup")
    return BorgBackupExecutor(settings)


def _build_notifier() -> Notifier:
    """Assemble the notifier.

    Raises:
        ConfigurationError: if Telegram is not configured.
    """

    settings = _require(load_telegram_bot_settings(), "Telegram bot")
    return TelegramNotifier(settings)


def _require[T](component: T | None, name: str) -> T:
    """Return the component, or fail loudly if it was not configured.

    Raises:
        ConfigurationError: if the component is None.
    """

    if component is None:
        raise ConfigurationError(
            f"{name} is not configured. Check the required environment variables."
        )

    return component
