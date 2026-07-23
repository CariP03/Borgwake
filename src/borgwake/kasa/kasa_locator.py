"""Implementation of a locator for Kasa plugs."""

import logging
from typing import override

from kasa import Discover

from borgwake.kasa.kasa_loader import KasaSettings
from borgwake.networking.device_locator import DeviceAddress, DeviceLocator
from borgwake.networking.identifiers import compare_mac

logger = logging.getLogger(__name__)


class PlugDiscoveryError(RuntimeError):
    """An error occurred when trying to discover Kasa plug."""

    pass


class KasaLocator(DeviceLocator):
    """Locator for Kasa plugs."""

    def __init__(self, settings: KasaSettings):
        self._settings = settings

    @override
    async def locate_device(self) -> DeviceAddress | None:
        """Scan the network to find a Kasa plug with the given MAC and credentials in the network."""

        logger.info("Initializing Kasa plug discovery...")

        try:
            devices = await Discover.discover(credentials=self._settings.credentials)
        except Exception as e:
            logger.critical(
                "Unexpected error during Kasa network discovery.", exc_info=True
            )
            raise PlugDiscoveryError("Failed to communicate with the network.") from e

        for ip, device in devices.items():
            if compare_mac(device.mac, self._settings.plug_mac):
                logger.debug("Found searched plug with IP %s, MAC %s", ip, device.mac)

                return DeviceAddress(ip=ip, mac=device.mac)

        logger.debug("No plug found on network with MAC %s", self._settings.plug_mac)
        return None
