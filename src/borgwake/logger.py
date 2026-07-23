"""Logging initialization for Borgwake."""

import logging
import os
from dataclasses import dataclass
from datetime import date, datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

_PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]
_DEFAULT_LOG_DIR = _PROJECT_ROOT / "logs"


@dataclass(frozen=True)
class LoggingSettings:
    """Where Borgwake's logs live."""

    log_dir: Path
    log_file: Path


def load_logging_settings() -> LoggingSettings:
    """Load logging settings from the environment, with sensible defaults."""

    log_dir = Path(os.getenv("LOG_DIR", _DEFAULT_LOG_DIR))
    log_file = log_dir / "borgwake.log"
    return LoggingSettings(log_dir, log_file)


def setup_logging(settings: LoggingSettings) -> None:
    """Configures the global logging system for the application.

    Sets up the global root logger with both console output and daily
    rotating file handlers, including fallback logic for intermittent execution.

    Has the side effect of creating the logging directory if this does not exist.
    """

    settings.log_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] [%(name)s] %(message)s"
    )

    fh = TimedRotatingFileHandler(settings.log_file, when="D", backupCount=7)
    fh.setFormatter(formatter)
    root_logger.addHandler(fh)

    # Force rollover in containers.
    if settings.log_file.exists():
        edit_time = datetime.fromtimestamp(settings.log_file.stat().st_mtime).date()
        if edit_time < date.today():
            fh.doRollover()

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)
