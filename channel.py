import asyncio
from datetime import datetime
from asyncio import StreamWriter, StreamReader
from typing import Dict

from api import StreamInfoApi
from chatters import Chatters
from irc import Irc
from ratelimit import privmsg_ratelimit_async
from config import cfg


class Channel:
    def __init__(self, name, irc, bot=None):
        self.irc: Irc = irc
        self.name: str = name
        self.chatters: Chatters = Chatters(self.name)
        self.is_mod = False
        self.stats = StreamInfoApi(cfg.client_id, self.name)

        from bots import BaseBot
        self.bot: BaseBot = bot

        channels[self.name.lower()] = self

        asyncio.get_event_loop().create_task(self.update_loop())
        
    @property
    def live(self):
        return self.stats.started_at != datetime.min

    async def send_message(self, msg):
        privmsg = f'PRIVMSG #{self.name} :{msg}'

        if self.bot is not None:
            await self.bot.on_privmsg_sent(msg, self)

        await self.send_raw(privmsg)

    async def send_command(self, cmd):
        await self.send_raw(f'/{cmd}')

    @privmsg_ratelimit_async
    async def send_raw(self, msg):
        self.irc.send(msg)

    async def ban(self, user):
        await self.send_raw(f'/ban {user}')

    async def update_loop(self):
        while True:
            await self.chatters.update()
            await self.stats.update()
            self.is_mod = cfg.nick.lower() in self.chatters.mods
            await asyncio.sleep(60)

    def __str__(self):
        return f'<Channel name={repr(self.name)}>'


channels: Dict[str, Channel] = {}
