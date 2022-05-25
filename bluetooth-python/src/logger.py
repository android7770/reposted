import logging
from typing import Final, NoReturn

logging.basicConfig(filename='bluetooth.plugin.log', level=logging.INFO)

logger: Final = logging.getLogger('com.sobolevn.bluetooth')


def fail(message: str) -> NoReturn:
    """Fails something with `RuntimeError` and logs an error message."""
    logger.critical(message)
    raise RuntimeError(message)
