import shlex
import typing

from typing import Union
from ..regex import RE_AT_MENTION

__all__ = ('split_message', 'get_message_mentions', 'join_args_to_original_string')

# little "hack" to get around circular imports for type hinting
if typing.TYPE_CHECKING:
    from ..message import Message


def split_message(msg: str):
    try:
        return shlex.split(msg)
    except ValueError:
        return msg.split(' ')


def get_message_mentions(message: Union['Message', str]):
    # hack to get around circular imports
    from ..message import Message

    # try getting the attribute "content", if it fails, text is set to the passed message itself
    # which should be a string
    text = getattr(message, 'content', message)
    mentions = tuple(map(str.lower, RE_AT_MENTION.findall(text)))

    # checks for username mentions without the @
    if isinstance(message, Message):
        mentions += tuple(p.lower() for p in message.parts if p in message.channel.chatters)

    return mentions


def join_args_to_original_string(args: typing.Iterable[str]) -> str:
    return ' '.join(f'"{value}"' if any(v.isspace() for v in args) else value for value in args)
