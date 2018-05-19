import shlex

from irc import Irc
from ratelimit import whisper_ratelimit_async


@whisper_ratelimit_async
async def send_whisper(irc: Irc, user: str, msg: str):
    irc.send(f'PRIVMSG #{user} :/w {user} {msg}')


def split_message(msg: str):
    try:
        return shlex.split(msg)
    except ValueError:
        return msg.split(' ')
