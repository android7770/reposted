import asyncio
from typing import Final, final

import objc
from CoreBluetooth import (
    CBCentralManager,
    CBManagerStatePoweredOff,
    CBManagerStatePoweredOn,
)
from Foundation import NSObject
from libdispatch import DISPATCH_QUEUE_SERIAL, dispatch_queue_create
from logger import logger
from stream_deck import StreamDeckExchange

_ToggleStates: Final = frozenset((
    CBManagerStatePoweredOff,  # 4
    CBManagerStatePoweredOn,  # 5
))
_CBCentralManagerDelegate: Final = objc.protocolNamed(
    'CBCentralManagerDelegate',
)
_QUEUE_NAME: Final = b'com.sobolevn.bluetooth'


@final
class CentralManagerDelegate(NSObject):  # type: ignore
    """Instance of CBCentralManagerDelegate."""

    _exchange: StreamDeckExchange
    _loop: asyncio.BaseEventLoop

    @objc.python_method
    def init_with_exchange(
        self,
        exchange: StreamDeckExchange,
        loop: asyncio.BaseEventLoop,
    ) -> 'CentralManagerDelegate':
        """Initializes and sets extra props. Use this method."""
        self.init()
        self._exchange = exchange
        self._loop = loop
        return self

    # PyObjC API:

    ___pyobjc_protocols__ = [_CBCentralManagerDelegate]

    def init(self) -> 'CentralManagerDelegate':
        """Init function for NSObject."""
        instance = objc.super(CentralManagerDelegate, self).init()

        manager = CBCentralManager.alloc()
        instance.central_manager = manager.initWithDelegate_queue_(
            instance,
            dispatch_queue_create(_QUEUE_NAME, DISPATCH_QUEUE_SERIAL),
        )
        return instance

    def centralManagerDidUpdateState_(  # noqa: N802, WPS120
        self,
        central_manager: CBCentralManager,
    ) -> None:
        """Executed when bluetooth is enabled/disabled in system settings."""
        state = central_manager.state()
        logger.info('Got bluetooth state change to {0}'.format(state))
        if state in _ToggleStates:
            asyncio.run_coroutine_threadsafe(
                self._exchange.notify_state_change(state),
                self._loop,
            )
