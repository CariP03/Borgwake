"""Contains functions to operate on network entities.

These functions validate, clean network or compare entities such as IP or MAC addresses.
"""

import re
import ipaddress


def validate_ip(ip: str) -> bool:
    """Validates IPv4 address."""

    try:
        ipaddress.ip_address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def validate_mac(mac: str) -> bool:
    """Validates MAC address."""

    if re.match("[0-9a-f]{12}$", _clean_mac(mac)):
        return True
    return False


def compare_mac(mac1: str, mac2: str) -> bool:
    """Compare MAC address."""

    return _clean_mac(mac1) == _clean_mac(mac2)


def _clean_mac(mac: str) -> str:
    """Clean MAC address.

    Normalize MAC address to lowercase, remove leading and trailing spaces and
    remove separators.
    """

    return mac.replace(":", "").replace("-", "").replace(" ", "").lower()
