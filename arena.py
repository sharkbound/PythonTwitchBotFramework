from typing import List
from asyncio import Future, ensure_future

from channel import Channel
from irc import Irc


class Arena:
    def __init__(self, channel, entry_fee=30, active_time_seconds=30, min_users=2):
        self.channel: Channel = channel
        self.entry_fee: int = entry_fee
        self.active_time_seconds: int = active_time_seconds
        self.min_users: int = min_users
        self.users: List[str] = []
        self.future: Future = None

    async def _start_arena_countdown(self):
        pass

    async def _start_arena(self):
        if len(self.users) < self.min_users:
            #todo
            # await self.channel.send_message()
            pass

    def start(self):
        self.future = ensure_future(self._start_arena_countdown())
