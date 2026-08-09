"""Provides an SSH shutdown mechanism."""

import asyncio
import os
from dataclasses import dataclass
from logging import getLogger

from borgwake.fields import parse_field
from borgwake.networking.reachability_checker import ReachabilityChecker
from borgwake.power.abstractions import ShutdownFailure, TurnableOff

logger = getLogger(__name__)

_DEFAULT_SHUTDOWN_TIME = 60  # in seconds


@dataclass(frozen=True)
class SSHShutdownSettings:
    """Settings for the SSH shutdown mechanism."""

    ssh_username: str
    ssh_timeout: int


def load_ssh_shutdown_settings() -> SSHShutdownSettings | None:
    """Load SSH shutdown settings from the environment.

    Returns None if SSH_USERNAME is not set.

    Raises:
        EnvConfigurationError: if an env variable is set but invalid.
    """

    ssh_username = os.getenv("SSH_USERNAME")

    if ssh_username is None:
        return None

    raw_ssh_timeout = os.getenv("SHUTDOWN_TIME", _DEFAULT_SHUTDOWN_TIME)
    ssh_timeout = parse_field(raw_ssh_timeout, int, "shutdown timeout")

    return SSHShutdownSettings(ssh_username, ssh_timeout)


class SSHShutdown(TurnableOff):
    """Shutdown mechanism via SSH."""

    def __init__(
        self,
        settings: SSHShutdownSettings,
        host_name: str,
        reachability_checker: ReachabilityChecker,
    ):
        self._settings = settings
        self._host_name = host_name
        self._reachability_checker = reachability_checker

    async def turn_off(self) -> None:
        """Shut down the remote host via SSH and confirm it went offline.

        Raises:
            ShutdownFailure: if the SSH command fails or the host never
                goes offline within the configured timeout.
        """

        logger.info("Attempting graceful shutdown via SSH")

        try:
            process = await asyncio.create_subprocess_exec(
                "ssh",
                f"{self._settings.ssh_username}@{self._host_name}",
                "sudo shutdown -h now",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            return_code = await process.wait()

            if return_code != 0:
                raise ShutdownFailure(
                    f"SSH shutdown command exited with code {return_code}."
                )

            logger.info("Waiting for host to shutdown...")
            await asyncio.sleep(self._settings.ssh_timeout)

            if await self._reachability_checker.is_online():
                raise ShutdownFailure(
                    f"Host {self._host_name} is still reachable after shutdown timeout."
                )

            logger.info("Remote host turned off successfully")

        except OSError as e:
            logger.exception("Failed to execute SSH command.")
            raise ShutdownFailure("Failed to shut down via SSH.") from e
