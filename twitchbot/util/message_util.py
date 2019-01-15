import shlex
import typing
from typing import Union

from ..regex import RE_AT_MENTION

# little "hack" to get around circular imports for type hinting
if typing.TYPE_CHECKING:
    from ..message import Message


def split_message(msg: str):
    try:
        return shlex.split(msg)
    except ValueError:
        return msg.split(' ')


def get_message_mentions(message: Union['Message', str]):
    # try getting the attribute "content", if it fails, text is set to the passed message itself
    text = getattr(message, 'content', message)
    return tuple(RE_AT_MENTION.findall(text))
