import objc
from typing import Final, final
import asyncio
from Foundation import NSObject
from CoreBluetooth import CBCentralManager, CBManagerStatePoweredOff, CBManagerStatePoweredOn
from libdispatch import dispatch_queue_create, DISPATCH_QUEUE_SERIAL
from stream_deck import StreamDeckExchange
from logger import logger

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
    _exchange: StreamDeckExchange

    @objc.python_method
    def init_with_exchange(
        self, 
        exchange: StreamDeckExchange,
        loop: asyncio.BaseEventLoop,
    ) -> 'CentralManagerDelegate':
        self.init()
        self._exchange = exchange
        self._loop = loop
        return self

    # PyObjC API:

    ___pyobjc_protocols__ = [_CBCentralManagerDelegate]

    def init(self) -> 'CentralManagerDelegate':
        """MacOS init function for NSObject."""
        self = objc.super(CentralManagerDelegate, self).init()
        self.central_manager = CBCentralManager.alloc().initWithDelegate_queue_(
            self, 
            dispatch_queue_create(_QUEUE_NAME, DISPATCH_QUEUE_SERIAL),
        )
        return self

    def centralManagerDidUpdateState_(
        self, 
        centralManager: CBCentralManager,
    ) -> None:
        state = centralManager.state()
        logger.info('Got bluetooth state change to {0}'.format(state))
        if state in _ToggleStates:
            asyncio.run_coroutine_threadsafe(
                self._exchange.notify_state_change(state), 
                self._loop,
            )
