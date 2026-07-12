"""Locate the remote host's IP address, either from static config or via ARP scan."""

import logging
import time

from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import srp

from src.borgwake.config import HOST_STATIC_IP, REMOTE_HOST_MAC, SUBNET
from src.borgwake.utils.network import compare_mac

logger = logging.getLogger(__name__)

_CACHE_TTL_SECONDS = 300

_cached_host: str | None = None
_cached_at: float = 0.0


def _find_ip_by_mac(
    target_mac: str,
    subnet: str | None = None,
    attempts: int = 6,
    timeout: int = 4,
) -> str | None:
    """Scan the subnet using ARP to find the IP associated with a MAC address."""

    if subnet is None:
        subnet = SUBNET

    arp = ARP(pdst=subnet)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    try:
        for i in range(attempts):
            logger.debug(
                "Attempt %s/%s: Scanning subnet %s for MAC %s",
                i + 1,
                attempts,
                subnet,
                target_mac,
            )

            result = srp(packet, timeout=timeout, verbose=False)[0]
            for sent, received in result:
                if compare_mac(received.hwsrc, target_mac):
                    logger.info("Found IP: %s for MAC: %s", received.psrc, target_mac)

                    return received.psrc

            time.sleep(1)

        logger.warning(
            "Failed to find IP for MAC %s after %s attempts.", target_mac, attempts
        )

        return None

    except Exception:
        logger.warning("Error while searching IP for MAC %s", target_mac, exc_info=True)
        return None


def get_host_ip(force_refresh: bool = False) -> str | None:
    """Get the host IP from static configuration, or via a cached ARP scan.

    If HOST_STATIC_IP is set, it is always used and never expires.
    Otherwise, the ARP-resolved IP is cached for _CACHE_TTL_SECONDS to avoid
    re-scanning on every call, but re-resolved after expiry or when
    force_refresh is True (e.g. after a failed ping) to pick up IP changes.
    """

    global _cached_host, _cached_at

    if HOST_STATIC_IP:
        return HOST_STATIC_IP

    cache_expired = (time.monotonic() - _cached_at) > _CACHE_TTL_SECONDS
    if _cached_host is None or cache_expired or force_refresh:
        logger.info("Scanning network for MAC: %s", REMOTE_HOST_MAC)

        resolved = _find_ip_by_mac(REMOTE_HOST_MAC)
        if resolved is not None:
            _cached_host = resolved
            _cached_at = time.monotonic()
        elif cache_expired:
            # Scan failed and old cache is stale: don't keep serving it.
            _cached_host = None

    return _cached_host
