from typing import List, Tuple, TYPE_CHECKING, Optional, Callable, Awaitable

from twitchbot import get_bot
from .util import get_message_mentions
from .channel import Channel, channels
from .irc import Irc
from .regex import RE_PRIVMSG, RE_WHISPER, RE_USER_JOIN, RE_USERNOTICE, RE_USER_PART
from .enums import MessageType
from .util import split_message
from .tags import Tags
from .emote import emotes, Emote
from .config import cfg

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
        self.system_message: Optional[str] = None
        self.bot: 'BaseBot' = bot
        self.reward: Optional[str] = None
        self.msg_id: Optional[str] = None

        self._parse()

    def _parse(self):
        # this weird looking bit is to make sure we do not do unnecessary checks when we have found a match
        # it takes advantage of the fact that python's `or` works as true check/default value provider
        # if the first check is false, it tries the next, then if thats false, it tries the next one, and it keeps doing this
        # until one matches or it run out of functions to check
        (self._parse_usernotice()
         or self._parse_privmsg()
         or self._parse_whisper()
         or self._parse_user_join()
         or self._parse_user_part()
         or self._check_ping())

        if self.parts and any(p in emotes for p in self.parts):
            self.emotes = tuple(emotes[p] for p in self.parts if p in emotes)

        if self.tags is not None and 'system-msg' in self.tags.all_tags:
            self.system_message = self.tags.all_tags['system-msg'].replace(r'\s', ' ')

        self.msg_id = (self.tags.all_tags.get('msg-id')
                       if self.tags is not None
                       else None)

    def _parse_user_part(self) -> bool:
        m = RE_USER_PART.search(self.raw_msg)
        if m:
            self.channel = channels[m['channel']]
            self.author = m['user']
            self.type = MessageType.USER_PART

        return bool(m)

    def _parse_user_join(self) -> bool:
        m = RE_USER_JOIN.search(self.raw_msg)
        if m:
            # ensure the channel exists, if it does not, create it and put it in the cache
            channel_name = m['channel']
            if channel_name not in channels:
                Channel(channel_name, irc=self.irc, register_globally=True).start_update_loop()

            self.channel = channels[channel_name]
            self.author = m['user']
            self.type = MessageType.USER_JOIN

        return bool(m)

    def _parse_whisper(self) -> bool:
        m = RE_WHISPER.search(self.raw_msg)
        if m:
            self.author = m['user']
            self.receiver = m['receiver']
            self.content = m['content']
            self.type = MessageType.WHISPER
            self.parts = split_message(self.content)
            self.channel = Channel(self.author, self.irc, register_globally=False)

        return bool(m)

    def _parse_privmsg(self) -> bool:
        m = RE_PRIVMSG.search(self.raw_msg)
        if m:
            self.channel = channels[m['channel']]
            self.author = m['user']
            self.content = m['content']
            self.type = MessageType.PRIVMSG
            self.parts = split_message(self.content)
            self.tags = Tags(m['tags'])
            self.mentions = get_message_mentions(self)

            # checking if its a channel point redemption
            self.reward = self.tags.all_tags.get('msg-id') or self.tags.all_tags.get('custom-reward-id')
            if self.reward is not None:
                self.type = MessageType.CHANNEL_POINTS_REDEMPTION

        return bool(m)

    def _parse_usernotice(self) -> bool:
        m = RE_USERNOTICE.search(self.raw_msg)
        if m:
            self.tags = Tags(m['tags'])
            self.channel = channels[m['channel']]
            self.author = self.tags.all_tags.get('login')
            self.content = m['content']
            if self.tags.msg_id in {'sub', 'resub', 'subgift', 'anonsubgift', 'submysterygift', 'anongiftpaidupgrade',
                                    'giftpaidupgrade'}:
                self.type = MessageType.SUBSCRIPTION
            elif self.tags.msg_id == 'raid':
                self.type = MessageType.RAID
                self.author = self.tags.all_tags.get('msg-param-login')
            else:
                self.type = MessageType.USER_NOTICE

        return bool(m)

    def _check_ping(self) -> bool:
        if self.raw_msg == 'PING :tmi.twitch.tv':
            self.type = MessageType.PING

        return self.type is MessageType.PING

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
    def is_raid(self):
        return self.type is MessageType.RAID

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

        if self.type is MessageType.PRIVMSG and (not whisper or cfg.disable_whispers):
            await self.channel.send_message(msg)

        elif self.type is MessageType.WHISPER or (whisper and self.type is MessageType.PRIVMSG):
            if self.irc is None:
                raise RuntimeError('no irc instance set for this message')

            await self.irc.send_whisper(self.author, msg)

        # else:
        #     raise ValueError(f'invalid message type to reply, expected PRIVMSG or WHISPER, current: {self.type}')

    async def wait_for_reply(self, predicate: Callable[['Message'], Awaitable[bool]] = None, timeout=30, default=None,
                             raise_on_timeout=False) -> 'Message':
        """
        waits for a message matching `predicate` to be received, when its received, it returns that message.

        if no message matching `predicate` is received by the timeout, the default will be returned.

        if raise_on_timeout is True and no matching message is received, this function will raise asyncio.TimeoutError

        if raise_on_timeout is False and no matching message is received, default will be returned when it times-out

        default is by default is None
        raise_on_timeout by default is False
        predicate defaults to `same_author_predicate`
        """

        from .replywaiter import wait_for_reply, same_author_predicate

        return await wait_for_reply(predicate or same_author_predicate(self), timeout=timeout, default=default,
                                    raise_on_timeout=raise_on_timeout)

    def __str__(self):
        if self.type is MessageType.PRIVMSG:
            return f'{self.author}({self.channel.name}): {self.content}'

        elif self.type is MessageType.WHISPER:
            return f'{self.author} -> {self.receiver}: {self.content}'

        elif self.type is MessageType.PING:
            return 'PING'

        elif self.type is MessageType.SUBSCRIPTION:
            return f'{self.author} subscribed to {self.channel_name}: {self.system_message}'

        elif self.type is MessageType.RAID:
            return f'{self.author} has raided {self.channel_name} with {self.tags.raid_viewer_count} viewers!'

        elif self.type is MessageType.USER_NOTICE:
            return f'USERNOTICE for {self.author}'

        elif self.type is MessageType.USER_JOIN:
            return f'{self.author} joined {self.channel_name}'

        elif self.type is MessageType.USER_PART:
            return f'{self.author} left {self.channel_name}'

        elif self.type is MessageType.CHANNEL_POINTS_REDEMPTION:
            return f'{self.author} redeemed reward {self.reward} in #{self.channel_name}'

        return self.raw_msg

    def __getitem__(self, item):
        """
        if item is a slice, returns a space joined parts of that slice

        if item in a int, returns a single part at that index
        """
        if isinstance(item, int):
            return self.parts[item]

        return ' '.join(self.parts[item])

    def __len__(self):
        """
        :return: the len() of self.parts
        """
        return len(self.parts)
