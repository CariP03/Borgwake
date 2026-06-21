import os
from kasa import Discover, Credentials

from src.borgwake.utils.logger import logger


# raised when the plug initialization fails
class PlugInitError(Exception):
    pass


async def plug_init():
    logger.info(f"Initializing plug")
    try:
        creds = Credentials(os.getenv("EMAIL"), os.getenv("PASSWORD"))
        devices = await Discover.discover(credentials=creds)

        # find target device by MAC
        target_device = None
        for ip, device in devices.items():
            await device.update()
            if device.mac.lower() == os.getenv("PLUG_MAC").lower():
                logger.debug(f"Connecting to device with IP {ip}, MAC {device.mac} and alias {device.alias}")
                target_device = device
            else:
                logger.debug(f"Skipping device with IP {ip}, MAC {device.mac} and alias {device.alias}")
                await device.disconnect()

        if target_device:
            logger.info("Plug initialized successfully")
            return target_device

        raise PlugInitError(f"Device with MAC {os.getenv('PLUG_MAC')} not found")

    except PlugInitError:
        raise

    except Exception as e:
        logger.critical(f"Failed to create Plug instance: {str(e)}", exc_info=True)
        raise PlugInitError("Failed to create Plug instance") from e
