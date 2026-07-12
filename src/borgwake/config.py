"""Configuration file for Borgwake.

Declare constants, load them from the environment and validate the configuration.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from src.borgwake.utils.network import validate_ip, validate_subnet, validate_mac

# This is used in case environment variables have not been loaded by the system.
load_dotenv()


def _require(name: str) -> str:
    """Require a non-empty environment variable."""

    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value


def _optional(name: str) -> str | None:
    """Read an optional environment variable, treating empty string as unset."""

    return os.getenv(name) or None


def _validate_email(email: str) -> str:
    """Minimal email format validation."""

    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError(f"Invalid email address: {email}")
    return email


_PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

LOG_DIR: Path = Path(os.getenv("LOG_DIR", str(_PROJECT_ROOT / "logs")))
LOG_FILE: Path = LOG_DIR / "borgwake.log"

TELEGRAM_BOT_TOKEN: str | None = _optional("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID: str | None = _optional("TELEGRAM_CHAT_ID")

KASA_EMAIL: str = _validate_email(_require("KASA_EMAIL"))
KASA_PASSWORD: str = _require("KASA_PASSWORD")
KASA_PLUG_MAC: str = validate_mac(_require("KASA_PLUG_MAC"))
POWER_CYCLE_DELAY: int = int(os.getenv("POWER_CYCLE_DELAY", "30"))

REMOTE_HOST_MAC: str = validate_mac(_require("REMOTE_HOST_MAC"))
SUBNET: str = validate_subnet(os.getenv("SUBNET", "192.168.1.0/24"))
_host_static_ip: str | None = _optional("HOST_STATIC_IP")
HOST_STATIC_IP: str | None = validate_ip(_host_static_ip) if _host_static_ip else None
