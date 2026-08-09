"""Provides a locator for a device with a statically configured IP."""

import logging
import os
from typing import override

from borgwake.errors import ConfigurationError
from borgwake.fields import parse_field
from borgwake.networking.device_locator import DeviceAddress, DeviceLocator
from borgwake.networking.identifiers import validate_ip

logger = logging.getLogger(__name__)


def load_static_host_ip() -> str | None:
    """Load the static IP address.

    Returns None if HOST_STATIC_IP is not set.

    Raises:
        ConfigurationError: if an env variable is set but invalid.
    """

    raw_host_ip = os.getenv("REMOTE_HOST_STATIC_IP")
    if raw_host_ip is None:
        return None

    return parse_field(raw_host_ip, validate_ip, "remote host static IP")


class StaticIpLocator(DeviceLocator):
    """Locator that returns a statically configured IP address, without scanning the network."""

    def __init__(self, static_ip: str):
        self._static_ip = static_ip

    @override
    async def locate_device(self) -> DeviceAddress | None:
        """Return the statically configured IP address."""

        logger.debug("Using static IP: %s", self._static_ip)

        return DeviceAddress(mac="", ip=self._static_ip)
