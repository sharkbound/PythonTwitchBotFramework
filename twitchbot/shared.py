from typing import Optional, TYPE_CHECKING

__all__ = [
    'get_bot', 'set_bot'
]

if TYPE_CHECKING:
    from .bots import BaseBot

_bot: Optional['BaseBot'] = None


def get_bot() -> Optional['BaseBot']:
    return _bot


def set_bot(bot: 'BaseBot'):
    global _bot
    _bot = bot
