"""Definition of ARP locator, its settings and loader."""

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from typing import override

from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import srp

from borgwake.errors import ConfigurationError
from borgwake.networking.device_locator import DeviceAddress, DeviceLocator
from borgwake.networking.identifiers import compare_mac, validate_mac, validate_subnet

logger = logging.getLogger(__name__)

_DEFAULT_SUBNET = "192.168.1.0/24"
_DEFAULT_ATTEMPTS = 6
_DEFAULT_TIMEOUT = 4


@dataclass(frozen=True)
class ArpSettings:
    """Settings for ARP-based host locating."""

    target_mac: str
    subnet: str
    attempts: int
    timeout: int


def load_arp_settings() -> ArpSettings | None:
    """Load ARP locating settings from the environment.

    Returns None if REMOTE_HOST_MAC is not set.

    Raises:
        ConfigurationError: if an env variable is set but invalid.
    """

    raw_target_mac = os.getenv("REMOTE_HOST_MAC")
    if raw_target_mac is None:
        return None

    try:
        target_mac = validate_mac(raw_target_mac)
    except ValueError as e:
        raise ConfigurationError(
            f"Invalid REMOTE_HOST_MAC: {raw_target_mac!r}"
        ) from e

    raw_subnet = os.getenv("ARP_SUBNET", _DEFAULT_SUBNET)
    try:
        subnet = validate_subnet(raw_subnet)
    except ValueError as e:
        raise ConfigurationError(f"Invalid ARP_SUBNET: {raw_subnet!r}") from e

    raw_attempts = os.getenv("ARP_ATTEMPTS", _DEFAULT_ATTEMPTS)
    try:
        attempts = int(raw_attempts)
    except ValueError as e:
        raise ConfigurationError(
            f"Invalid ARP_ATTEMPTS: {raw_attempts!r} is not an integer."
        ) from e

    raw_timeout = os.getenv("ARP_TIMEOUT", _DEFAULT_TIMEOUT)
    try:
        timeout = int(raw_timeout)
    except ValueError as e:
        raise ConfigurationError(
            f"Invalid ARP_TIMEOUT: {raw_timeout!r} is not an integer."
        ) from e

    return ArpSettings(
        target_mac=target_mac,
        subnet=subnet,
        attempts=attempts,
        timeout=timeout,
    )


class ArpLocator(DeviceLocator):
    """Locator for the remote host via ARP scan."""

    def __init__(self, settings: ArpSettings):
        self._settings = settings

    @override
    async def locate_device(self) -> DeviceAddress | None:
        """Get the remote host's address via an ARP scan."""

        logger.info("Scanning network for MAC: %s", self._settings.target_mac)

        resolved = await asyncio.to_thread(self._scan_for_ip)
        if resolved is None:
            return None

        return DeviceAddress(mac=self._settings.target_mac, ip=resolved)

    def _scan_for_ip(self) -> str | None:
        """Scan the subnet using ARP to find the IP associated with the target MAC. Blocking."""

        arp = ARP(pdst=self._settings.subnet)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp

        try:
            for attempt in range(self._settings.attempts):
                logger.debug(
                    "Attempt %s/%s: Scanning subnet %s for MAC %s",
                    attempt + 1,
                    self._settings.attempts,
                    self._settings.subnet,
                    self._settings.target_mac,
                )

                result = srp(packet, timeout=self._settings.timeout, verbose=False)[0]
                for _, received in result:
                    if compare_mac(received.hwsrc, self._settings.target_mac):
                        logger.info(
                            "Found IP: %s for MAC: %s",
                            received.psrc,
                            self._settings.target_mac,
                        )
                        return received.psrc

                time.sleep(1)

            logger.warning(
                "Failed to find IP for MAC %s after %s attempts.",
                self._settings.target_mac,
                self._settings.attempts,
            )
            return None

        except Exception:
            logger.warning(
                "Error while searching IP for MAC %s",
                self._settings.target_mac,
                exc_info=True,
            )
            return None
