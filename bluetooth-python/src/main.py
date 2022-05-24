import argparse
from delegate import CentralManagerDelegate
from stream_deck import StreamDeckExchange
import asyncio
from typing import Protocol
from logger import logger


class _ParsedArgs(Protocol):
    port: int
    plugin_uuid: str
    register_event: str


def _parse_cli_args() -> _ParsedArgs:
    """
    Parse args passed by SteamDeck.

    They'll be set by the Stream Deck desktop software 
    when it launches our plugin.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-port', type=int)
    parser.add_argument(
        '-pluginUUID',
        dest='plugin_uuid',
        type=str, 
    )
    parser.add_argument(
        '-registerEvent',
        dest='register_event',
        type=str,
    )

    # Ignore unknown args in case a Stream Deck update 
    # adds optional flags later.
    (known_args, _) = parser.parse_known_args()
    return known_args


if __name__ == '__main__':
    logger.info('Starting')
    args = _parse_cli_args()
    logger.info('Got args: {0}'.format(args))

    loop = asyncio.get_event_loop()
    exchange = StreamDeckExchange()
    delegate = CentralManagerDelegate.alloc().init_with_exchange(exchange, loop)  

    try:
        loop.run_until_complete(
            exchange.start(
                port=args.port,
                plugin_uuid=args.plugin_uuid,
                register_event=args.register_event,
            ),
        )
    except Exception as exc:
        logger.critical(exc)
        raise
