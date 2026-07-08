"""Telegram notification services for backup monitoring."""

import logging

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from src.borgwake.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


async def send_backup_result(status: int) -> None:
    """Send backup result message.

    Args:
        status (int): Backup status code.
            If 0 the backup is successful.
            If 1 the backup completed with warnings.
            Else the backup completed with errors.
    """

    if status == 0:
        text = "🟢 Backup completed *SUCCESSFULLY*!"
    elif status == 1:
        text = "🟡 Backup completed with *WARNINGS*! Check logs for more details."
    else:
        text = "🔴 Backup completed with *ERRORS*! Check logs for more details."

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        logger.info(f"Sending message to Telegram chat: {text}")

        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        try:
            async with bot:
                await bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN
                )
        except TelegramError as e:
            logger.error("Failed to send message to Telegram.", exc_info=e)

    else:
        logger.info("Telegram Bot not configured. No message will be sent.")
