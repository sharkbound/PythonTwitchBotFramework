from asyncio import sleep, ensure_future, get_event_loop
from collections import deque
from functools import wraps
from collections import namedtuple

# DelayedCall = namedtuple('DelayedCall', 'func args kwargs')

PRIVMSG_MAX_MOD = 100
PRIVMSG_MAX_NORMAL = 20

WHISPER_MAX = 10

privmsg_sent = 0
whisper_sent = 0


# privmsg_queue = deque()
# whisper_queue = deque()


def privmsg_ratelimit_async(func):
    @wraps(func)
    async def _wrapper(*args, **kwargs):
        global privmsg_sent

        while privmsg_sent >= PRIVMSG_MAX_MOD:
            await sleep(1)

        privmsg_sent += 1
        await func(*args, **kwargs)

    return _wrapper


def whisper_ratelimit_async(func):
    @wraps(func)
    async def _wrapper(*args, **kwargs):
        global whisper_sent

        while whisper_sent >= WHISPER_MAX:
            await sleep(1)

        whisper_sent += 1
        await func(*args, **kwargs)

    return _wrapper


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


get_event_loop().create_task(privmsg_sent_reset_loop())
get_event_loop().create_task(whisper_sent_reset_loop())
