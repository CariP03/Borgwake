"""Contains the logging setup function."""

import logging
from datetime import date, datetime
from logging.handlers import TimedRotatingFileHandler

from src.borgwake.config import LOG_DIR, LOG_FILE


def setup_logging():
    """Configures the global logging system for the application."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] [%(name)s] %(message)s"
    )

    fh = TimedRotatingFileHandler(LOG_FILE, when="D", backupCount=7)
    fh.setFormatter(formatter)
    root_logger.addHandler(fh)

    # Force rollover in containers.
    if LOG_FILE.exists():
        edit_time = datetime.fromtimestamp(LOG_FILE.stat().st_mtime).date()
        if edit_time < date.today():
            fh.doRollover()

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)
