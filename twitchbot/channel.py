import asyncio
import typing
from datetime import datetime
from typing import Dict

from .api import StreamInfoApi
from .api.chatters import Chatters
from .config import get_nick, get_client_id
from .data import UserFollowers
from .permission import perms
from .shared import get_bot
from .util import get_user_followers, get_headers, strip_twitch_command_prefix, normalize_string

if typing.TYPE_CHECKING:
    from .bots import BaseBot
    from .irc import Irc


class Channel:
    def __init__(self, name, irc: 'Irc', register_globally=True):
        self.irc: 'Irc' = irc
        self.name: str = normalize_string(name)
        self.chatters: Chatters = Chatters(self.name)
        self.is_vip: bool = False
        self.is_mod: bool = False
        self.stats: StreamInfoApi = StreamInfoApi(get_client_id(), self.name)
        self.bot: 'BaseBot' = get_bot()

        if register_globally:
            channels[self.name.lower()] = self
            perms.load_permissions(name)

    async def followers(self) -> UserFollowers:
        return await get_user_followers(self.name, get_headers())

    @property
    def live(self):
        return self.stats.started_at != datetime.min

    async def send_message(self, msg: str, strip_command_prefix: bool = False):
        if strip_command_prefix:
            msg = strip_twitch_command_prefix(msg)

        await self.irc.send_privmsg(self.name, msg)

    async def send_command(self, cmd: str):
        await self.irc.send_privmsg(self.name, f'/{cmd}')

    # async def ban(self, user):
    #     await self.send_command(f'ban {user}')

    async def update_loop(self):
        from .config import cfg
        if get_client_id() != 'CLIENT_ID':
            while True:
                await self.chatters.update()
                await self.stats.update()
                self.is_mod = get_nick().lower() in self.chatters.mods
                self.is_vip = get_nick().lower() in self.chatters.vips
                await asyncio.sleep(120)  # update viewers every 2 minutes

    async def ban(self, user: str, reason: str = ''):
        """purges a user's messages then permabans them from the channel"""
        await self.send_command(f'ban {user} {reason}')

    async def timeout(self, user: str, duration: int = 600):
        """
        purges a user's messages then times out the user (makes them unable to chat)
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

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name.lower() == other.lower()

        if isinstance(other, Channel):
            return self.name.lower() == other.name.lower()

        return False


channels: Dict[str, Channel] = {}


# DummyChannel is a placeholder channel for when the bots sends a whisper
class DummyChannel:
    __slots__ = 'name', 'is_mod', 'is_vip'

    def __init__(self, name):
        self.name = name
        self.is_vip = False
        self.is_mod = False
