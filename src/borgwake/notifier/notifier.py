"""Provides the abstract interface every notifier implements."""

from abc import ABC, abstractmethod

from borgwake.borg.abstractions import BackupStatus


class Notifier(ABC):
    """Abstraction of a notifier."""

    @abstractmethod
    async def notify(self, status: BackupStatus) -> None:
        """Send a notification to an external service."""

