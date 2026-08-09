"""Definition of settings for a kasa plug and its loader."""

import os
from dataclasses import dataclass

from kasa import Credentials

from borgwake.errors import ConfigurationError
from borgwake.fields import parse_field
from borgwake.networking.identifiers import validate_mac

_DEFAULT_POWER_CYCLE_DELAY = 10


@dataclass(frozen=True)
class KasaSettings:
    """Settings for a kasa plug."""

    credentials: Credentials
    plug_mac: str
    power_cycle_delay: int


def load_kasa_settings() -> KasaSettings | None:
    """Load kasa plug settings from the environment.

    Raises:
        EnvConfigurationError: if environment variables are partially configured or invalid.
    """

    kasa_email = os.getenv("KASA_EMAIL")
    kasa_password = os.getenv("KASA_PASSWORD")
    kasa_plug_mac = os.getenv("KASA_PLUG_MAC")
    kasa_power_cycle_delay = os.getenv("KASA_POWER_CYCLE_DELAY", _DEFAULT_POWER_CYCLE_DELAY)

    if kasa_email is None and kasa_password is None and kasa_plug_mac is None:
        return None

    if kasa_email is None or kasa_password is None or kasa_plug_mac is None:
        raise ConfigurationError(
            "Kasa Plug is partially configured: All KASA_EMAIL, KASA_PASSWORD and KASA_PLUG_MAC must be set."
        )

    kasa_email = parse_field(kasa_email, _validate_email, "Kasa e-mail")
    kasa_plug_mac = parse_field(kasa_plug_mac, validate_mac, "Kasa plug MAC")
    kasa_power_cycle_delay = parse_field(kasa_power_cycle_delay, int, "Kasa power cycle delay")

    return KasaSettings(Credentials(kasa_email, kasa_password), kasa_plug_mac, kasa_power_cycle_delay)


def _validate_email(email: str) -> str:
    """Minimal email format validation."""

    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError(f"Invalid email address: {email}")

    return email
