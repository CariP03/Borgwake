"""Abstractions for power state."""

from abc import ABC, abstractmethod


class TurnableOn(ABC):
    """Abstractions for turning a device on."""

    @abstractmethod
    async def turn_on(self) -> None:
        """Turn device on.

        Raises:
            TurnOnFailure: if the device could not be turned on.
        """


class TurnableOff(ABC):
    """Abstractions for turning a device off."""

    @abstractmethod
    async def turn_off(self) -> None:
        """Turn device off.

        Raises:
            ShutdownFailure: if the device could not be turned off.
                May be raised as PartialShutdownFailure or TotalShutdownFailure.
        """


class TurnOnFailure(Exception):
    """The turn on operation failed."""


class ShutdownFailure(Exception):
    """Base exception for the TurnableOff exception."""


class PartialShutdownFailure(ShutdownFailure):
    """Some shutdown steps succeeded, some failed."""


class TotalShutdownFailure(ShutdownFailure):
    """All shutdown steps failed."""

    def __init__(self, message: str, errors: list[Exception] | None = None):
        super().__init__(message)
        self.errors = errors or []
