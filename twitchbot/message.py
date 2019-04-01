from typing import List, Tuple, TYPE_CHECKING, Optional
from .util import get_message_mentions
from twitchbot.channel import Channel, channels
from .irc import Irc
from .regex import RE_PRIVMSG, RE_WHISPER, RE_JOINED_CHANNEL, RE_USERNOTICE
from .enums import MessageType
from .util import split_message
from .tags import Tags
from .emote import emotes, Emote

if TYPE_CHECKING:
    from .bots import BaseBot


class Message:
    def __init__(self, msg, irc=None, bot=None):
        self.channel: Optional[Channel] = None
        self.author: Optional[str] = None
        self.content: Optional[str] = None
        self.parts: List[str] = []
        self.type: MessageType = MessageType.NONE
        self.raw_msg: str = msg
        self.receiver: Optional[str] = None
        self.irc: Irc = irc
        self.tags: Optional[Tags] = None
        self.emotes: List[Emote] = []
        self.mentions: Tuple[str] = ()
        self.bot: 'BaseBot' = bot

        self._parse()

    def _parse(self):
        m = RE_USERNOTICE.search(self.raw_msg)
        if m:
            self.tags = Tags(m['tags'])
            self.channel = channels[m['channel']]
            self.author = self.tags.all_tags.get('login')
            self.content = m['content']
            if self.tags.msg_id in {'sub', 'resub', 'subgift', 'anonsubgift', 'submysterygift'}:
                self.type = MessageType.SUBSCRIPTION

        m = RE_PRIVMSG.search(self.raw_msg)
        if m:
            self.channel = channels[m['channel']]
            self.author = m['user']
            self.content = m['content']
            self.type = MessageType.PRIVMSG
            self.parts = split_message(self.content)
            self.tags = Tags(m['tags'])
            self.mentions = get_message_mentions(self)

        m = RE_WHISPER.search(self.raw_msg)
        if m:
            self.author = m['user']
            self.receiver = m['receiver']
            self.content = m['content']
            self.type = MessageType.WHISPER
            self.parts = split_message(self.content)

        m = RE_JOINED_CHANNEL.search(self.raw_msg)
        if m:
            self.channel = channels[m['channel']]
            self.author = m['user']
            self.type = MessageType.JOINED_CHANNEL

        elif self.raw_msg == 'PING :tmi.twitch.tv':
            self.type = MessageType.PING

        if self.parts and any(p in emotes for p in self.parts):
            self.emotes = tuple(emotes[p] for p in self.parts if p in emotes)

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
    def is_subscription(self):
        return self.type is MessageType.SUBSCRIPTION

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

        if not isinstance(msg, str):
            msg = str(msg)

        if self.type is MessageType.PRIVMSG and not whisper:
            await self.channel.send_message(msg)

        elif self.type is MessageType.WHISPER or (whisper and self.type is MessageType.PRIVMSG):
            if self.irc is None:
                raise ValueError('no irc instance set for this message')

            await self.irc.send_whisper(self.author, msg)

        # else:
        #     raise ValueError(f'invalid message type to reply, expected PRIVMSG or WHISPER, current: {self.type}')

    def __str__(self):
        if self.type is MessageType.PRIVMSG:
            return f'{self.author}({self.channel.name}): {self.content}'

        elif self.type is MessageType.WHISPER:
            return f'{self.author} -> {self.receiver}: {self.content}'

        elif self.type is MessageType.PING:
            return 'PING'

        return self.raw_msg

    def __len__(self):
        """
        :return: the len() of self.parts
        """
        return len(self.parts)
