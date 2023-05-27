import asyncio
import json
from typing import Any, Dict, Final, Optional, Tuple, Union, final

import bluetooth
from logger import logger
from websockets.legacy.client import WebSocketClientProtocol
from websockets.legacy.client import connect as ws_connect

_WS_URI_TEMPLATE: Final = 'ws://localhost:{port}'
_WS_PAYLOAD: Final = '{"event": "willAppear"}'
_JsonType = Dict[str, Any]


@final
class StreamDeckExchange(object):
    """Websocket event exchange with Elgato StreamDeck."""

    def __init__(self) -> None:
        """Nothing fancy here."""
        self._websocket: Optional[WebSocketClientProtocol] = None
        self._context: Optional[str] = None
        self._controller = _BluetoothMessageController()
        self._bluetooth_state: Optional[int] = None

    async def start(
        self,
        port: int,
        register_event: str,
        plugin_uuid: str,
    ) -> None:
        """Run websocket and listen for events."""
        self._websocket = await ws_connect(_WS_URI_TEMPLATE.format(port=port))
        logger.info('Websocket connection is created on port {0}'.format(port))

        # Complete the mandatory Stream Deck Plugin registration procedure:
        await self._send_message({
            'event': register_event,
            'uuid': plugin_uuid,
        })
        logger.info('Plugin registration is succesful')

        asyncio.create_task(  # type: ignore[unused-awaitable]
            self._update_periodically(0.1),
        )

        try:  # noqa: WPS501
            # This is an infinite loop until the connection dies:
            await self._message_receive_loop()
        finally:
            await self._websocket.close()

    async def _update_periodically(self, period: float) -> None:
        # Technically, this loop never ends, but that's the whole point.
        while True:  # noqa: WPS457
            await asyncio.sleep(period)
            await self._process_inbound_message(_WS_PAYLOAD)

    async def _message_receive_loop(self) -> None:
        """
        Waiting for and processing inbound websocket messages.

        Until the connection dies.
        """
        assert self._websocket is not None, 'Please, call `.start()` first'
        async for message in self._websocket:
            await self._process_inbound_message(message)

    async def _process_inbound_message(
        self,
        message: Union[str, bytes],
    ) -> None:
        if isinstance(message, bytes):
            message = message.decode('utf-8')

        # You can log the message here, but it take a lot of space on disk:
        parsed = json.loads(message)

        self._maybe_store_context(parsed)
        reply = self._controller.handle_event(parsed, self._context)
        if reply is not None and self._bluetooth_state != reply[0]:
            self._bluetooth_state = reply[0]
            await self._send_message(reply[1])

    async def _send_message(self, payload: _JsonType) -> None:
        assert self._websocket is not None, 'Please, call `.start()` first'

        await self._websocket.send(json.dumps(payload))
        logger.info('Sent payload: {0}'.format(payload))

    def _maybe_store_context(self, payload: _JsonType) -> None:
        context = payload.get('context')
        if context is not None and context != self._context:
            self._context = context
            logger.info('Got new plugin context: {0}'.format(context))


@final
class _BluetoothMessageController(object):
    def handle_event(
        self,
        payload: _JsonType,
        context: Optional[str],
    ) -> Optional[Tuple[int, _JsonType]]:
        event_type = payload['event']
        if event_type == 'keyUp':
            self._handle_key_up()
        elif event_type == 'willAppear':
            return self._handle_will_appear(context)
        return None

    def _handle_key_up(self) -> None:
        bluetooth.toggle_bluetooth_state()

    def _handle_will_appear(
        self,
        context: Optional[str],
    ) -> Optional[Tuple[int, _JsonType]]:
        if context is None:
            return None  # We don't have a context yet to send a message.

        state = bluetooth.get_bluetooth_state()
        return state, {
            'event': 'setState',
            'context': context,
            'payload': {
                'state': state,
            },
        }
