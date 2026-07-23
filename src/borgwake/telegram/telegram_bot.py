"""Telegram notification service for backup monitoring."""

import logging
import os
from dataclasses import dataclass
from typing import override

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from borgwake.errors import ConfigurationError
from borgwake.notifier.notifier import Notifier, Status

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TelegramBotSettings:
    """Settings for telegram bot."""

    bot_token: str
    chat_id: str


def load_telegram_bot_settings() -> TelegramBotSettings | None:
    """Load telegram bot settings from the environment.

    Raises:
        EnvConfigurationError: if environment variables are partially configured.
    """

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if bot_token is None and chat_id is None:
        return None

    if bot_token is None or chat_id is None:
        raise ConfigurationError(
            "Telegram Bot is partially configured: Both TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set."
        )

    return TelegramBotSettings(bot_token, chat_id)


def _get_message_text(status: Status) -> str:
    """Parse the status in a Telegram Markdown message."""

    match status:
        case Status.SUCCESS:
            return "🟢 Backup completed *SUCCESSFULLY*!"
        case Status.WARNING:
            return "🟡 Backup completed with *WARNINGS*! Check logs for more details."
        case Status.ERROR:
            return "🔴 Backup completed with *ERRORS*! Check logs for more details."
        case _:
            raise TypeError(f"Unknown status: {status}")


class TelegramNotifier(Notifier):
    """Telegram notifier for backup monitoring."""

    def __init__(self, settings: TelegramBotSettings):
        self._settings = settings

    @override
    async def notify(self, status: Status) -> None:
        text = _get_message_text(status)

        logger.info(f"Sending the following message to Telegram chat: {text}")

        bot = Bot(token=self._settings.bot_token)
        try:
            async with bot:
                await bot.send_message(
                    chat_id=self._settings.chat_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                )
        except TelegramError as e:
            logger.error("Failed to send message to Telegram.", exc_info=e)
