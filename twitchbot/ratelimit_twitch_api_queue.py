import asyncio
import time
import typing
from typing import NamedTuple

__all__ = [
    'TwitchApiRatelimitQueue'
]

if typing.TYPE_CHECKING:
    from twitchbot import RateLimit


class _TwitchApiUrl(NamedTuple):
    url: str
    headers: dict
    future: asyncio.Future


class TwitchApiRatelimitQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.requests_left = 0
        self.limit = -1
        self.ratelimit_reset = -1

    def update_ratelimit_reset(self, ratelimit: 'RateLimit'):
        self.ratelimit_reset = ratelimit.reset
        self.requests_left = ratelimit.remaining
        self.limit = ratelimit.limit

    @property
    def current_ratelimited(self):
        # not currently ratelimited if the reset time is in the past, or no reset is epoch time is set
        if self.ratelimit_reset < time.time() or self.ratelimit_reset == -1:
            return False

        if self.requests_left <= 0:
            return True

        return False

    def append_url_request(self, url: str, headers: dict) -> asyncio.Future:
        fut = asyncio.Future()
        self.queue.put_nowait(_TwitchApiUrl(url=url, headers=headers, future=fut))
        return fut
