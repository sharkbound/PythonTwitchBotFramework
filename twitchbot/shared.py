from typing import Optional, TYPE_CHECKING

__all__ = [
    'get_bot',
    'set_bot',
    'get_pubsub',
]

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
