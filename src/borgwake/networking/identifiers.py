"""Network utilities for entity validation and comparison.

Provide functions to validate, clean and compare network entities such as IP or MAC addresses.
"""

import ipaddress
import re


def is_valid_ip(ip: str) -> bool:
    """Validates an IP address."""

    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def validate_ip(ip: str) -> str:
    """Validates an IP address.

    Raises:
        ValueError: If IP address is invalid.
    """

    if not is_valid_ip(ip):
        raise ValueError(f"Invalid IP address: {ip}")

    return ip


def is_valid_mac(mac: str) -> bool:
    """Validates MAC address."""

    return bool(re.match("[0-9a-f]{12}$", clean_mac(mac)))


def validate_mac(mac: str) -> str:
    """Validates a MAC address.

    Raises:
        ValueError: If the MAC address is invalid.
    """
    if not is_valid_mac(mac):
        raise ValueError(f"Invalid MAC address: {mac}")

    return mac


def is_valid_subnet(subnet: str) -> bool:
    """Validates a network in CIDR notation (e.g. '192.168.1.0/24')."""

    try:
        ipaddress.ip_network(subnet)
        return True
    except ValueError:
        return False


def validate_subnet(subnet: str) -> str:
    """Validates a subnet in CIDR notation.

    Raises:
        ValueError: If the subnet is invalid.
    """
    if not is_valid_subnet(subnet):
        raise ValueError(f"Invalid subnet: {subnet}")

    return subnet


def compare_mac(mac1: str, mac2: str) -> bool:
    """Compare MAC address."""

    return clean_mac(mac1) == clean_mac(mac2)


def clean_mac(mac: str) -> str:
    """Clean MAC address.

    Normalize MAC address to lowercase, remove leading and trailing spaces and
    remove separators.
    """

    return mac.replace(":", "").replace("-", "").replace(" ", "").lower()
