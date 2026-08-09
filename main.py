import asyncio
import logging
import sys

from dotenv import load_dotenv

from borgwake.composition_root import compose
from borgwake.errors import ConfigurationError, HostResolutionError
from borgwake.logger import (
    default_logging_settings,
    load_logging_settings,
    setup_logging,
)
from borgwake.notifier.notifier import NotifierError
from borgwake.power.abstractions import ShutdownFailure

logger = logging.getLogger(__name__)


async def main() -> int:
    try:
        logger_settings = load_logging_settings()
    except ConfigurationError as e:
        logger_settings = default_logging_settings()
        setup_logging(logger_settings)

        logging.getLogger(__name__).error("Failed to load logging settings: %s", e)
        return 1

    setup_logging(logger_settings)

    try:
        status = await compose()
        logger.info("Workflow completed with status: %s", status)
        return 0
    except ExceptionGroup as eg:
        for exc in eg.exceptions:
            logger.error("A failure occurred: %s", exc, exc_info=exc)
        return 1
    except (
        ShutdownFailure,
        NotifierError,
        ConfigurationError,
        HostResolutionError,
    ) as e:
        logger.error("A failure occurred: %s", e, exc_info=e)
        return 1


if __name__ == "__main__":
    load_dotenv()
    sys.exit(asyncio.run(main()))
