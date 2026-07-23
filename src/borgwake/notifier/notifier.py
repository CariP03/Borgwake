"""Provides the abstract interface every notifier implements."""

from abc import ABC, abstractmethod

from borgwake.status import Status


class Notifier(ABC):
    """Abstraction of a notifier."""

    @abstractmethod
    async def notify(self, status: Status) -> None:
        """Send a notification to an external service."""

        pass
