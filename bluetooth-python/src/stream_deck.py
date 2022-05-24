from typing import Final, Optional, final, Dict, Any, Union
from websockets.legacy.client import connect as ws_connect, WebSocketClientProtocol
import json
import bluetooth
from logger import logger
import uuid

_WS_URI: Final = 'ws://127.0.0.1:{port}'
_JsonType = Dict[str, Any]


@final
class StreamDeckExchange(object):
    def __init__(self) -> None:
        self._websocket: Optional[WebSocketClientProtocol] = None
        self._controller = _BluetoothMessageController()

    async def start(
        self, 
        port: int, 
        register_event: str, 
        plugin_uuid: str,
    ) -> None:
        self._websocket = await ws_connect(_WS_URI.format(port=port))
        logger.info('Websocket connection is created on port {0}'.format(port))

        # Complete the mandatory Stream Deck Plugin registration procedure:
        await self._send_message({
            'event': register_event,
            'uuid': plugin_uuid
        })
        logger.info('Plugin registration is succesful')

        try:
            # This is an infinite loop until the connection dies:
            await self._message_receive_loop()
        finally:
            await self._websocket.close()

    async def notify_state_change(self, state: int) -> None:
        await self._process_inbound_message('{"event": "willAppear"}')

    async def _message_receive_loop(self) -> None:
        """
        Waiting for and processing inbound websocket messages.

        Until the connection dies.
        """
        assert self._websocket is not None, 'Please, call `.start()` first'
        async for message in self._websocket:
            try:
                await self._process_inbound_message(message)
            except Exception as exc:
                # Some things might go wrong during this process.
                # We don't want the whole thing to fail. 
                # So, just log the error.
                logger.error(exc)

    async def _process_inbound_message(
        self, 
        message: Union[str, bytes],
    ) -> None:
        if isinstance(message, bytes):
            message = message.decode('utf-8')

        logger.info('Got ws message: {0}'.format(message))

        parsed = json.loads(message)
        reply = self._controller.handle_event(parsed)
        if reply is not None:
            await self._send_message(reply)

    async def _send_message(self, payload: _JsonType) -> None:
        assert self._websocket is not None, 'Please, call `.start()` first'
        await self._websocket.send(json.dumps(payload))
        logger.info('Sent payload: {0}'.format(payload))


@final
class _BluetoothMessageController(object):
    def handle_event(self, payload: _JsonType) -> Optional[_JsonType]:
        event_type = payload['event']
        if event_type == 'keyUp':
            self._handle_key_up()
        elif event_type == 'willAppear':
            return self._handle_will_appear()
        return None

    def _handle_key_up(self) -> None:
        bluetooth.toggle_bluetooth_state()
    
    def _handle_will_appear(self) -> _JsonType:
        return {
            'event': 'setState',
            'context': str(uuid.uuid4()),
            'payload': {
                'state': bluetooth.get_bluetooth_state(),
            },
        }
