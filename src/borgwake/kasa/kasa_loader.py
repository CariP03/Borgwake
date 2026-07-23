"""Definition of settings for a kasa plug and its loader."""

import os
from dataclasses import dataclass

from kasa import Credentials

from borgwake.errors import EnvConfigurationError
from borgwake.networking.identifiers import validate_mac


@dataclass(frozen=True)
class KasaSettings:
    """Settings for a kasa plug."""

    credentials: Credentials
    plug_mac: str


def load_kasa_settings() -> KasaSettings | None:
    """Load kasa plug settings from the environment.

    Raises:
        EnvConfigurationError: if environment variables are partially configured or invalid.
    """

    kasa_email = os.getenv("KASA_EMAIL")
    kasa_password = os.getenv("KASA_PASSWORD")
    kasa_plug_mac = os.getenv("KASA_PLUG_MAC")

    if kasa_email is None and kasa_password is None and kasa_plug_mac is None:
        return None

    if kasa_email is None or kasa_password is None or kasa_plug_mac is None:
        raise EnvConfigurationError(
            "Kasa Plug is partially configured: All KASA_EMAIL, KASA_PASSWORD and KASA_PLUG_MAC must be set."
        )

    try:
        kasa_email = _validate_email(kasa_email)
    except ValueError as e:
        raise EnvConfigurationError(f"Invalid Kasa e-mail: {kasa_email!r}") from e
    try:
        kasa_plug_mac = validate_mac(kasa_plug_mac)
    except ValueError as e:
        raise EnvConfigurationError(f"Invalid Kasa plug MAC: {kasa_plug_mac!r}") from e

    return KasaSettings(Credentials(kasa_email, kasa_password), kasa_plug_mac)


def _validate_email(email: str) -> str:
    """Minimal email format validation."""

    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError(f"Invalid email address: {email}")

    return email
