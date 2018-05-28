import asyncio
from datetime import datetime
from typing import Dict
from .irc import Irc
from .config import cfg
from .permission import perms
from .chatters import Chatters
from .api import StreamInfoApi


class Channel:
    def __init__(self, name, irc, bot=None, register_globally=True):
        self.irc: Irc = irc
        self.name: str = name
        self.chatters: Chatters = Chatters(self.name)
        self.is_mod = False
        self.stats = StreamInfoApi(cfg.client_id, self.name)

        from twitchbot.bots import BaseBot
        self.bot: BaseBot = bot

        if register_globally:
            channels[self.name.lower()] = self
            perms.load_permissions(name)

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
        purges a user's messages then timeout out (makes them unable to chat) for the specified duration (default 600 seconds)
        """
        await self.send_command(f'timeout {user} {duration}')

    async def color(self, color: str):
        """sets the bots chat color"""
        await self.send_command(f'color {color}')

    def __str__(self):
        return f'<Channel name={repr(self.name)}>'


channels: Dict[str, Channel] = {}
