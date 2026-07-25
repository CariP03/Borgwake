"""Provides the abstract interface every notifier implements."""

from abc import ABC, abstractmethod

from borgwake.backup.abstractions import BackupStatus


class NotifierError(Exception):
    """An error occurred while trying to send a notification."""


class Notifier(ABC):
    """Abstraction of a notifier."""

    @abstractmethod
    async def notify(self, status: BackupStatus) -> None:
        """Send a notification to an external service.

        Raises:
            NotifierError: if an error occurred while sending the notification.
        """
