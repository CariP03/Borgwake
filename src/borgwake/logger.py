"""Logging initialization for Borgwake."""

import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from borgwake.fields import parse_field

_PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
_DEFAULT_LOG_DIR = _PROJECT_ROOT / "logs"

_VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
_DEFAULT_LOG_LEVEL = "INFO"


class _ThirdPartyLogFilter(logging.Filter):
    """Suppresses third-party (non-Borgwake) log records below WARNING."""

    def filter(self, record: logging.LogRecord) -> bool:
        is_ours = record.name.startswith("borgwake") or record.name == "__main__"
        return is_ours or record.levelno >= logging.WARNING


@dataclass(frozen=True)
class LoggingSettings:
    """Where Borgwake's logs live."""

    log_dir: Path
    log_file: Path
    log_level: str


def load_logging_settings() -> LoggingSettings:
    """Load logging settings from the environment, with sensible defaults."""

    log_dir = Path(os.getenv("LOG_DIR", _DEFAULT_LOG_DIR))
    log_file = log_dir / "borgwake.log"

    raw_log_level = os.getenv("LOG_LEVEL", _DEFAULT_LOG_LEVEL)
    log_level = parse_field(raw_log_level, _validate_log_level, "logging level")

    return LoggingSettings(log_dir, log_file, log_level)


def default_logging_settings() -> LoggingSettings:
    """Returns hardcoded, always-valid logging settings for bootstrapping."""

    return LoggingSettings(
        log_dir=_DEFAULT_LOG_DIR,
        log_file=_DEFAULT_LOG_DIR / "borgwake.log",
        log_level=_DEFAULT_LOG_LEVEL,
    )


def setup_logging(settings: LoggingSettings) -> None:
    """Configures the global logging system for the application.

    Sets up the global root logger with both console output and daily
    rotating file handlers, including fallback logic for intermittent execution.

    Has the side effect of creating the logging directory if this does not exist.
    """

    settings.log_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] [%(name)s] %(message)s"
    )

    third_party_filter = _ThirdPartyLogFilter()

    fh = TimedRotatingFileHandler(settings.log_file, when="D", backupCount=7)
    fh.setFormatter(formatter)
    fh.addFilter(third_party_filter)
    root_logger.addHandler(fh)

    # Force rollover in containers.
    if settings.log_file.exists():
        edit_time = datetime.fromtimestamp(
            settings.log_file.stat().st_mtime, tz=UTC
        ).date()
        if edit_time < datetime.now(tz=UTC).date():
            fh.doRollover()

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.addFilter(third_party_filter)
    root_logger.addHandler(sh)


def _validate_log_level(log_level: str) -> str:
    """Validate the log level."""

    log_level = log_level.upper()
    if log_level not in _VALID_LOG_LEVELS:
        raise ValueError(f"Invalid log level: {log_level}")

    return log_level
