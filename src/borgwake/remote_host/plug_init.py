"""Smart plug abstraction for remote host power management"""

import asyncio
import logging

from kasa import Credentials, Discover, SmartDevice

from borgwake.utils.network import compare_mac
from src.borgwake.config import (
    KASA_EMAIL,
    KASA_PASSWORD,
    KASA_PLUG_MAC,
    POWER_CYCLE_DELAY,
)

logger = logging.getLogger(__name__)


class PlugError(Exception):
    """A plug error occurred"""

    pass


class KasaPlugHandler:
    """Handler for a Kasa plug.

    Handles connection, state, and power operations for the plug.
    """

    def __init__(self):
        self._device: SmartDevice | None = None
        self._plug_mac: str = KASA_PLUG_MAC
        self._credentials: Credentials = Credentials(KASA_EMAIL, KASA_PASSWORD)

    async def connect(self) -> None:
        """Discover the network and connect to the configured smart plug."""

        logger.info("Initializing Kasa plug discovery...")

        try:
            devices = await Discover.discover(credentials=self._credentials)
        except Exception as e:
            logger.critical(
                "Unexpected error during Kasa network discovery.", exc_info=True
            )
            raise PlugError("Failed to communicate with the network.") from e

        for ip, device in devices.items():
            if compare_mac(device.mac, self._plug_mac):
                logger.debug("Connecting to device with IP %s, MAC %s", ip, device.mac)

                await device.update()
                self._device = device

                break
            else:
                logger.debug(
                    "Skipping unrelated device with IP %s and MAC %s", ip, device.mac
                )

        if not self._device:
            raise PlugError(
                f"Device with MAC {self._plug_mac} not found on the network."
            )

        logger.info("Plug initialized successfully.")

    async def power_cycle(self) -> None:
        """Turn off the plug, wait for the configured delay, and turn it back on."""

        if not self._device:
            raise PlugError("Plug not initialized. Call connect() first.")

        logger.info("Executing power cycle on the plug...")

        try:
            await self._device.turn_off()
            logger.debug(
                "Plug turned OFF. Waiting for %s seconds...", POWER_CYCLE_DELAY
            )

            await asyncio.sleep(POWER_CYCLE_DELAY)

            await self._device.turn_on()
            await self._device.update()

            logger.info("Power cycle completed successfully.")

        except Exception as e:
            logger.critical("Error during plug power cycle.", exc_info=True)
            raise PlugError("Failed to execute power cycle.") from e

    async def turn_off(self) -> None:
        """Turn off the smart plug."""

        if not self._device:
            raise PlugError("Plug not initialized. Call connect() first.")

        try:
            await self._device.turn_off()
            await self._device.update()

            logger.info("Plug turned OFF successfully.")

        except Exception as e:
            logger.error("Failed to turn off plug.", exc_info=True)
            raise PlugError("Failed to turn off the smart plug.") from e

    async def disconnect(self) -> None:
        """Safely disconnect from the smart plug."""

        if self._device:
            try:
                await self._device.disconnect()
                logger.info("Plug disconnected successfully.")
            except Exception:
                logger.error(
                    "Error occurred while disconnecting the plug", exc_info=True
                )
            finally:
                self._device = None
