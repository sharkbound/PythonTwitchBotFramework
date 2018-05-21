import asyncio
from datetime import datetime
from typing import Dict
from api import StreamInfoApi
from chatters import Chatters
from irc import Irc
from config import cfg


class Channel:
    def __init__(self, name, irc, bot=None, register_globally=True):
        self.irc: Irc = irc
        self.name: str = name
        self.chatters: Chatters = Chatters(self.name)
        self.is_mod = False
        self.stats = StreamInfoApi(cfg.client_id, self.name)

        from bots import BaseBot
        self.bot: BaseBot = bot

        if register_globally:
            channels[self.name.lower()] = self

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
        while True:
            await self.chatters.update()
            await self.stats.update()
            self.is_mod = cfg.nick.lower() in self.chatters.mods
            await asyncio.sleep(60)

    def start_update_loop(self):
        asyncio.get_event_loop().create_task(self.update_loop())

    def __str__(self):
        return f'<Channel name={repr(self.name)}>'


channels: Dict[str, Channel] = {}
