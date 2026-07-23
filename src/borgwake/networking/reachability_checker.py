"""Provides a mechanism to check if a remote host is online."""

import asyncio
import logging

logger = logging.getLogger(__name__)

_PING_NUMBER = 4
_PING_TIMEOUT = 2
_POLL_TIMEOUT = 90
_POLL_INTERVAL = 10


class ReachabilityCheckError(Exception):
    """A system error occurred while checking if a remote host is online."""


class ReachabilityChecker:
    """Reachability mechanism to check if a remote host is online."""

    def __init__(self, host_name: str):
        self._host_name = host_name

    async def is_online(self) -> bool:
        """Check if remote host is online using ping command.

        Returns:
            True if the host is reachable, False if it is not reachable.
        Raises:
            ReachabilityCheckError: if a system error occurred while checking if remote host is online.
        """

        logger.info("Checking if remote host %s is online...", self._host_name)

        try:
            process = await asyncio.create_subprocess_exec(
                "ping",
                "-c",
                str(_PING_NUMBER),
                "-W",
                str(_PING_TIMEOUT),
                self._host_name,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            return_code = await process.wait()

            if return_code != 0:
                logger.info("Remote host %s is offline", self._host_name)
                return False

            logger.info("Remote host %s is online", self._host_name)
            return True

        except OSError as e:
            raise ReachabilityCheckError(
                "An error occurred while checking if remote host is online."
            ) from e

    async def wait_until_online(self) -> bool:
        """Poll the host until it responds or the timeout elapses.

        Returns:
            True if the host became reachable, False if the timeout was reached.
        Raises:
            ReachabilityCheckError: if a system error occurred while checking if remote host is online.
        """

        deadline = asyncio.get_event_loop().time() + _POLL_TIMEOUT
        while asyncio.get_event_loop().time() < deadline:
            if await self.is_online():
                return True
            await asyncio.sleep(_POLL_INTERVAL)
        return False
