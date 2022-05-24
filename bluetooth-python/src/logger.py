import logging
from typing import Final

logging.basicConfig(filename='bluetooth.plugin.log', level=logging.INFO)

logger: Final = logging.getLogger('com.sobolevn.bluetooth')
