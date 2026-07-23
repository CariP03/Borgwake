"""Provides a sequential shutdown strategy."""

from borgwake.power.abstractions import (
    PartialShutdownFailure,
    ShutdownFailure,
    TotalShutdownFailure,
    TurnableOff,
)


class SequentialShutdown(TurnableOff):
    """Sequential shutdown mechanism."""

    def __init__(self, first: TurnableOff, second: TurnableOff):
        self._first = first
        self._second = second

    async def turn_off(self) -> None:
        """Turn off devices following sequential shutdown.

        Raises:
            TotalShutdownFailure: if both devices failed to turn off.
            PartialShutdownFailure: if one device failed to turn off.
        """

        first_error: ShutdownFailure | None = None

        try:
            await self._first.turn_off()
        except ShutdownFailure as e:
            first_error = e

        try:
            await self._second.turn_off()
        except ShutdownFailure as second_error:
            if first_error:
                raise TotalShutdownFailure(
                    "Both devices failed to turn off", [first_error, second_error]
                ) from second_error
            else:
                raise PartialShutdownFailure(
                    "Second device failed to turn off"
                ) from second_error

        if first_error:
            raise PartialShutdownFailure(
                "First device failed to turn off"
            ) from first_error
