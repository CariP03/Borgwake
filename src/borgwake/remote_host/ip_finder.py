import os
from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import srp
import time

from src.borgwake.utils.logger import logger

_cached_host = None


def find_ip_by_mac(target_mac, subnet=None, attempts=6, timeout=4):
    if subnet is None:
        subnet = os.getenv("SUBNET", "192.168.1.0/24")

    arp = ARP(pdst=subnet)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    try:
        for i in range(attempts):
            logger.debug(f"Attempt {i + 1}/{attempts}: Scanning subnet {subnet} for MAC {target_mac}")
            result = srp(packet, timeout=timeout, verbose=False)[0]
            for sent, received in result:
                if received.hwsrc.lower() == target_mac.lower():
                    logger.info(f"Found IP: {received.psrc} for MAC: {target_mac}")
                    return received.psrc
            time.sleep(1)

        logger.warning(f"Failed to find IP for MAC {target_mac}")
        return None

    except Exception as e:
        logger.error(f"Error while searching IP for MAC {target_mac}: {str(e)}", exc_info=True)
        return None


def get_host_ip():
    global _cached_host
    if _cached_host is None:
        _cached_host = os.getenv("HOST_STATIC_IP")
        if _cached_host is not None:
            logger.info(f"Using static IP: {_cached_host}")
        else:
            _cached_host = find_ip_by_mac(os.getenv('REMOTE_HOST_MAC'))
    return _cached_host
