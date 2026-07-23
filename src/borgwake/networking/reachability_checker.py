"""Provides a mechanism to check if a remote host is online."""

import asyncio
import logging

logger = logging.getLogger(__name__)

_PING_NUMBER = 4
_PING_TIMEOUT = 2


class ReachabilityChecker:
    """Reachability mechanism to check if a remote host is online."""

    def __init__(self, host_name: str):
        self._host_name = host_name

    async def is_online(self) -> bool:
        """Check if remote host is online using ping command."""

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

        except OSError:
            logger.error("Failed to execute ping command.", exc_info=True)
            return False
