"""Provides a locator for a device with a statically configured IP."""

import logging
from typing import override

from borgwake.networking.device_locator import DeviceAddress, DeviceLocator

logger = logging.getLogger(__name__)


class StaticIpLocator(DeviceLocator):
    """Locator that returns a statically configured IP address, without scanning the network."""

    def __init__(self, static_ip: str):
        self._static_ip = static_ip

    @override
    async def locate_device(self) -> DeviceAddress | None:
        """Return the statically configured IP address."""

        logger.debug("Using static IP: %s", self._static_ip)

        return DeviceAddress(mac="", ip=self._static_ip)
