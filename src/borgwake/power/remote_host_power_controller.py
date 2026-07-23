"""Provides a unified power management facade for remote hosts."""

from typing import override

from borgwake.power.abstractions import TurnableOff, TurnableOn


class RemoteHostPowerController(TurnableOn, TurnableOff):
    """Facade that provides clients a simplified interface for remote power control."""

    def __init__(self, activator: TurnableOn, sleeper: TurnableOff):
        self._activator = activator
        self._sleeper = sleeper

    @override
    async def turn_on(self) -> None:
        await self._activator.turn_on()

    @override
    async def turn_off(self) -> None:
        await self._sleeper.turn_off()
