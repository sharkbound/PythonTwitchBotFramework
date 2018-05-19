import shlex
from typing import List

from channel import Channel, channels
from config import cfg
from irc import Irc
from regex import RE_PRIVMSG, RE_WHISPER
from enums import MessageType
from util import send_whisper, split_message


class Message:
    def __init__(self, msg, irc=None, bot=None):
        self.channel: Channel = None
        self.author: str = None
        self.content: str = None
        self.parts: List[str] = ()
        self.type: MessageType = MessageType.NONE
        self.raw_msg: str = msg
        self.receiver: str = None
        self.irc: Irc = irc

        from bots import BaseBot
        self.bot: BaseBot = bot

        m = RE_PRIVMSG.search(msg)
        if m is not None:
            self.channel = channels[m['channel']]
            self.author = m['user']
            self.content = m['content']
            self.type = MessageType.PRIVMSG
            self.parts = split_message(self.content)

        m = RE_WHISPER.search(msg)
        if m:
            self.author = m['user']
            self.receiver = m['receiver']
            self.content = m['content']
            self.type = MessageType.WHISPER
            self.parts = split_message(self.content)

        elif msg == 'PING :tmi.twitch.tv':
            self.type = MessageType.PING

    @property
    def is_user_message(self):
        return self.type in (MessageType.WHISPER, MessageType.PRIVMSG)

    @property
    def is_privmsg(self):
        return self.type is MessageType.PRIVMSG

    @property
    def is_whisper(self):
        return self.type is MessageType.WHISPER

    @property
    def mention(self):
        return f'@{self.author}' if self.author else ''

    @property
    def channel_name(self):
        if self.channel:
            return self.channel.name
        if self.author:
            return self.author
        return ''

    async def reply(self, msg: str = '', whisper=False):
        if not msg:
            raise ValueError('msg is empty, msg must be a non-empty string')

        if self.type is MessageType.PRIVMSG and not whisper:
            await self.channel.send_message(msg)

        elif self.type is MessageType.WHISPER or (whisper and self.type is MessageType.PRIVMSG):
            if self.irc is None:
                raise ValueError('no irc instance set for this message')

            await send_whisper(self.irc, self.author, msg)
            if self.bot is not None:
                await self.bot.on_whisper_sent(msg, self.author, cfg.nick)

        else:
            raise ValueError(f'invalid message type to reply, expected PRIVMSG or WHISPER, current: {self.type}')

    def __str__(self):
        if self.type is MessageType.PRIVMSG:
            return f'{self.author}({self.channel.name}): {self.content}'

        elif self.type is MessageType.WHISPER:
            return f'{self.author} -> {self.receiver}: {self.content}'

        elif self.type is MessageType.PING:
            return 'PING'

        return self.raw_msg
