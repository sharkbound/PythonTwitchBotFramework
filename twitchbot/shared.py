import socket
import websockets
from typing import Optional, TYPE_CHECKING

__all__ = [
    'get_bot',
    'set_bot',
    'get_pubsub',
    'WEBSOCKET_ERRORS',
]

WEBSOCKET_ERRORS = (
    websockets.ConnectionClosedError,
    websockets.ConnectionClosed,
    socket.gaierror,
    socket.error,
    ValueError,
    websockets.InvalidHandshake,
)

if TYPE_CHECKING:
    from .bots import BaseBot
    from .pubsub import PubSubClient

_bot: Optional['BaseBot'] = None


def get_bot() -> Optional['BaseBot']:
    return _bot


def set_bot(bot: 'BaseBot'):
    global _bot
    _bot = bot


def get_pubsub() -> 'PubSubClient':
    return get_bot().pubsub


TWITCH_IRC_WEBSOCKET_URL = 'wss://irc-ws.chat.twitch.tv:443'
