import asyncio
import time
import typing
import warnings
from json import JSONEncoder
from datetime import datetime
from typing import Dict

from .api import StreamInfoApi
from .api.chatters import Chatters
from .config import get_nick, get_client_id
from .data import UserFollowers
from .permission import perms
from .shared import get_bot
from .util import get_user_followers, get_headers, strip_twitch_command_prefix, normalize_string, send_announcement, send_shoutout, send_ban

if typing.TYPE_CHECKING:
    from .bots import BaseBot
    from .irc import Irc
    from .util import SendTwitchApiResponseStatus


class Channel:
    def __init__(self, name, irc: 'Irc', register_globally=True):
        self.irc: 'Irc' = irc
        self.name: str = normalize_string(name)
        self.chatters: Chatters = Chatters(self.name)
        self.is_vip: bool = False
        self.is_mod: bool = False
        self.stats: StreamInfoApi = StreamInfoApi(get_client_id(), self.name)
        self.bot: 'BaseBot' = get_bot()
        # epoch time of the last PRIVMSG message received on this channel
        self.last_privmsg_time: float = time.time()

        if register_globally:
            channels[self.name.lower()] = self
            perms.load_permissions(name)

    async def followers(self) -> UserFollowers:
        return await get_user_followers(self.name, get_headers())

    @property
    def live(self):
        return self.stats.started_at != datetime.min

    async def send_message(self, msg: str, strip_command_prefix: bool = False, _twitch_prefix: str = None):
        if strip_command_prefix:
            msg = strip_twitch_command_prefix(msg)

        await self.irc.send_privmsg(self.name, msg, _twitch_prefix=_twitch_prefix)

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
        warnings.warn(
            'sending bans via IRC is deprecated, please use `ban2` instead, which sends a twitch api request instead. If you are migrating from '
            'a previous PythonTwitchBotFramework version, the irc oauth may need to be regenerated via the token_utils.py script\nFor the api '
            'reference for the new ban endpoint see https://dev.twitch.tv/docs/api/reference/#ban-user', DeprecationWarning, stacklevel=2)

        raise RuntimeError(
            'sending bans via IRC is deprecated, please use `ban2` instead, which sends a twitch api request instead. If you are migrating from '
            'a previous PythonTwitchBotFramework version, the irc oauth may need to be regenerated via the token_utils.py script\nFor the api '
            'reference for the new ban endpoint see https://dev.twitch.tv/docs/api/reference/#ban-user')

    async def ban2(self, user: str, reason: str = '', timeout: int = None) -> 'SendTwitchApiResponseStatus':
        """purges a user's messages then bans a user a given time in seconds (1 - 1209600 [2 weeks]; default permanent) from the channel using twitch API"""
        return await send_ban(self.name, user, reason, timeout)

    async def timeout(self, user: str, duration: int = 600, reason: str = '') -> 'SendTwitchApiResponseStatus':
        """
        purges a user's messages then times out the user (makes them unable to chat)
        for the specified duration (default 600 seconds)
        """
        return await send_ban(self.name, user, reason, duration)

    async def purge(self, user: str) -> 'SendTwitchApiResponseStatus':
        """
        purges a user in the room (removes their messages via a 1 second timeout)
        :param user: user to purge
        """
        return await self.timeout(user, 1)

    async def color(self, color: str):
        """sets the bots chat color"""
        await self.send_command(f'color {color}')

    async def shoutout(self, target: str) -> 'SendTwitchApiResponseStatus':
        """
        Sends a shoutout to another streamer
        """
        return await send_shoutout(self.name, target)

    async def announcement(self, message: str, color: str = None) -> 'SendTwitchApiResponseStatus':
        """
        Creates an announcement with a message of maximum 500 chars and optional a color: blue, green, orange, purple
        """
        return await send_announcement(self.name, message, color)

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
