"""The DeviceLocator contract: its return DTO and the abstract interface every locator implements"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceAddress:
    """Mac and IP address of a device."""

    mac: str
    ip: str


class DeviceLocator(ABC):
    """Abstract class for device locator."""

    @abstractmethod
    async def locate_device(self) -> DeviceAddress | None:
        """Get both IP and MAC address of the device or None if the device could not be located."""
