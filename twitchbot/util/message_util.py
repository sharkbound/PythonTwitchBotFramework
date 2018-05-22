import shlex

from ..irc import Irc
from ..ratelimit import whisper_ratelimit_async


def split_message(msg: str):
    try:
        return shlex.split(msg)
    except ValueError:
        return msg.split(' ')
