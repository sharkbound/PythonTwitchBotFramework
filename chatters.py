import asyncio
from typing import Tuple

from dataclasses import dataclass

from util import get_channel_chatters


@dataclass()
class Chatters:
    channel: str
    mods: frozenset = frozenset()
    staff: frozenset = frozenset()
    admins: frozenset = frozenset()
    global_mods: frozenset = frozenset()
    viewers: frozenset = frozenset()
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
