"""Vendor specific implementation of a Kasa smart plug."""

import asyncio
import logging
from typing import override

from kasa import SmartDevice

from borgwake.power.abstractions import (
    ShutdownFailure,
    TurnableOff,
    TurnableOn,
    TurnOnFailure,
)

logger = logging.getLogger(__name__)


class KasaPlug(TurnableOn, TurnableOff):
    """Power-control operations for an already-connected Kasa smart plug."""

    def __init__(self, device: SmartDevice, power_cycle_delay: int):
        self._device = device
        self._power_cycle_delay = power_cycle_delay

    @override
    async def turn_on(self) -> None:
        """Power-cycles the plug to turn the downstream device on."""
        try:
            await self._device.turn_off()
            await self._device.update()
            await asyncio.sleep(self._power_cycle_delay)

            await self._device.turn_on()
            await self._device.update()

            logger.info("Plug power-cycled to turn device ON.")
        except Exception as e:
            logger.error("Failed to power-cycle plug for turn-on.", exc_info=True)
            raise TurnOnFailure("Failed to turn on the smart plug.") from e

    @override
    async def turn_off(self) -> None:
        try:
            await self._device.turn_off()
            await self._device.update()
            logger.info("Plug turned OFF successfully.")
        except Exception as e:
            logger.error("Failed to turn off plug.", exc_info=True)
            raise ShutdownFailure("Failed to turn off the smart plug.") from e
