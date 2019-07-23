import asyncio
import typing
from datetime import datetime
from typing import Dict

from .shared import get_bot
from .irc import Irc
from .config import cfg
from .permission import perms
from .api.chatters import Chatters
from .api import StreamInfoApi
from .util import get_user_followers, get_headers
from .data import UserFollowers

if typing.TYPE_CHECKING:
    from .bots import BaseBot


class Channel:
    def __init__(self, name, irc, register_globally=True):
        self.irc: Irc = irc
        self.name: str = name
        self.chatters: Chatters = Chatters(self.name)
        self.is_mod: bool = False
        self.stats: StreamInfoApi = StreamInfoApi(cfg.client_id, self.name)
        self.bot: 'BaseBot' = get_bot()

        if register_globally:
            channels[self.name.lower()] = self
            perms.load_permissions(name)

    async def followers(self) -> UserFollowers:
        return await get_user_followers(self.name, get_headers())

    @property
    def live(self):
        return self.stats.started_at != datetime.min

    async def send_message(self, msg):
        await self.irc.send_privmsg(self.name, msg)

    async def send_command(self, cmd):
        await self.irc.send_privmsg(self.name, f'/{cmd}')

    # async def ban(self, user):
    #     await self.send_command(f'ban {user}')

    async def update_loop(self):
        if cfg.client_id != 'CLIENT_ID':
            while True:
                await self.chatters.update()
                await self.stats.update()
                self.is_mod = cfg.nick.lower() in self.chatters.mods
                await asyncio.sleep(60)

    def start_update_loop(self):
        asyncio.get_event_loop().create_task(self.update_loop())

    async def ban(self, user: str, reason: str = ''):
        """purges a user's messages then permabans them from the channel"""
        await self.send_command(f'ban {user} {reason}')

    async def timeout(self, user: str, duration: int = 600):
        """
        purges a user's messages then timeout out (makes them unable to chat)
        for the specified duration (default 600 seconds)
        """
        await self.send_command(f'timeout {user} {duration}')

    async def purge(self, user: str):
        """
        purges a user in the room (removes their messages via a 1 second timeout)
        :param user: user to purge
        """
        await self.timeout(user, 1)

    async def color(self, color: str):
        """sets the bots chat color"""
        await self.send_command(f'color {color}')

    def __str__(self):
        return f'<Channel name={repr(self.name)}>'


channels: Dict[str, Channel] = {}


# DummyChannel is a placeholder channel for when the bots sends a whisper
class DummyChannel:
    def __init__(self, name):
        self.name = name
        self.is_mod = False
