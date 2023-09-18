from asyncio import sleep, get_event_loop

import typing
from collections import defaultdict
from datetime import datetime
from .util import add_nameless_task

if typing.TYPE_CHECKING:
    from .channel import Channel

__all__ = [
    'PRIVMSG_MAX_MOD',
    'PRIVMSG_MAX_NORMAL',
    'WHISPER_MAX',

    'privmsg_ratelimit',
    'privmsg_sent',
    'privmsg_sent_reset_loop',

    'whisper_ratelimit',
    'whisper_sent',
    'whisper_sent_reset_loop',
]

PRIVMSG_MAX_MOD = 100
PRIVMSG_MAX_NORMAL = 20
PRIVMSG_INTERVAL = 1

WHISPER_MAX = 10

privmsg_sent = 0
whisper_sent = 0

last_privmsg_sent_dt: typing.DefaultDict[str, datetime] = defaultdict(lambda: datetime.min)


def _get_last_privmsg_send_dt(channel: 'Channel') -> float:
    return (datetime.now() - last_privmsg_sent_dt[channel.name]).total_seconds()


async def privmsg_ratelimit(channel: 'Channel'):
    from .config import get_nick
    global privmsg_sent
    limit = PRIVMSG_MAX_NORMAL

    use_mod_limit = channel.is_mod or channel.is_vip or channel.name == get_nick()
    if use_mod_limit:
        limit = PRIVMSG_MAX_MOD

    while not use_mod_limit and _get_last_privmsg_send_dt(channel) < PRIVMSG_INTERVAL:
        await sleep(.3)

    while privmsg_sent >= limit:
        await sleep(1)

    privmsg_sent += 1
    last_privmsg_sent_dt[channel.name] = datetime.now()


async def whisper_ratelimit():
    global whisper_sent

    while whisper_sent >= WHISPER_MAX:
        await sleep(1)

    whisper_sent += 1


async def privmsg_sent_reset_loop():
    global privmsg_sent

    while True:
        privmsg_sent = 0
        await sleep(30)


async def whisper_sent_reset_loop():
    global whisper_sent

    while True:
        whisper_sent = 0
        await sleep(1)


add_nameless_task(privmsg_sent_reset_loop())
add_nameless_task(whisper_sent_reset_loop())
