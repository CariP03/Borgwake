import asyncio
import subprocess
import os
import time

from plug_init import plug_init, PlugInitError
from ip_finder import get_host_ip
from src.borgwake.utils.logger import logger

plug = None


# raised when unable to reach the host
class HostError(Exception):
    pass


async def __init_host():
    global plug
    try:
        plug = await plug_init()
    except PlugInitError as e:
        raise


# function that turn on the remote host by turning off the plug and then turning it on
async def __turn_on():
    logger.info("Turning on remote host")
    if plug is None:
        logger.critical(f"Plug not initialized")
        raise PlugInitError("Plug not initialized")

    try:
        # sleep for the time indicated before completing the power cycle
        delay = int(os.getenv("POWER_CYCLE_DELAY", 3))

        await plug.turn_off()
        await asyncio.sleep(delay)
        await plug.turn_on()
        await plug.update()

    except Exception as e:
        logger.critical(f"Error turning on plug: {e}", exc_info=True)
        raise


# check host status and turn it on if offline
async def start_host():
    await __init_host()

    was_online = True
    if not is_online():
        was_online = False
        await __turn_on()

        logger.info("Waiting for host to come online...")
        await asyncio.sleep(int(os.getenv('STARTUP_TIME')))  # waiting for host startup

        # check host status
        if not is_online():
            logger.critical(f"Unable to reach host", exc_info=True)
            raise HostError("Unable to reach host")
        else:
            logger.info("Host is online")

    return was_online


def is_online(count=4, timeout=2):
    logger.info("Checking if remote host is online")
    host = get_host_ip()
    if host is not None:

        # Windows systems
        # cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]

        # Linux systems
        cmd = ["ping", "-c", str(count), "-W", str(timeout), host]

        try:
            result = subprocess.run(cmd,
                                    check=True,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
            logger.info("Remote host is online")
            return True

        except subprocess.CalledProcessError as e:
            logger.warning(f"Ping failed: host is unreachable ({host})")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during ping: {e}", exc_info=True)
            return False

    logger.info("Remote host is offline (IP not found)")
    return False


def __shutdown_host(host):
    # soft shutdown
    logger.info("Attempting graceful shutdown via SSH")
    try:
        subprocess.run(["ssh", f"{os.getenv('SSH_USERNAME')}@{host}", "sudo shutdown -h now"], check=True)
        logger.info("Waiting for host to shutdown...")
        time.sleep(int(os.getenv('SHUTDOWN_TIME')))
        logger.info("Remote host turned off successfully")
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Failed to shut down host via SSH. Proceeding to turn off plug without graceful shutdown: {e}",
            exc_info=True)


async def turn_off():
    logger.info("Turning off remote host")
    if plug is None:
        logger.critical(f"Plug not initialized")
        raise PlugInitError("Plug not initialized")

    host = get_host_ip()
    if host is not None:
        __shutdown_host(host)
    else:
        logger.warning(f"Failed to find host IP. Proceeding to turn off plug without graceful shutdown")

    try:
        await plug.turn_off()
        await plug.update()
        logger.info("Plug turned off successfully")
    except Exception as e:
        logger.error(f"Failed to turn off plug: {e}", exc_info=True)


async def close_plug():
    if plug is not None:
        await plug.disconnect()
        logger.info(f"Plug disconnected")
