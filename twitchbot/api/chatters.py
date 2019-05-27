import asyncio
from typing import Tuple
from ..config import cfg

from dataclasses import dataclass

from twitchbot.util import get_channel_chatters


@dataclass
class Chatters:
    channel: str
    mods: frozenset = frozenset()
    staff: frozenset = frozenset()
    admins: frozenset = frozenset()
    global_mods: frozenset = frozenset()
    viewers: frozenset = frozenset()
    all_viewers: frozenset = frozenset()
    viewer_count: int = 0

    async def update(self):
        json = await get_channel_chatters(self.channel)
        chatters = json['chatters']

        self.mods = frozenset(chatters['moderators'])
        self.staff = frozenset(chatters['staff'])
        self.admins = frozenset(chatters['admins'])
        self.global_mods = frozenset(chatters['global_mods'])
        self.viewers = frozenset(chatters['viewers'])
        self.viewer_count = json['chatter_count']
        self.all_viewers = self.mods | self.staff | self.admins | self.global_mods | self.viewers | {self.channel}

    def __contains__(self, item):
        return item.lower() in self.all_viewers

    def __iter__(self):
        yield from self.all_viewers
