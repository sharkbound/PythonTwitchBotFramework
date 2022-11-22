import traceback
from datetime import datetime
from itertools import islice
from typing import List, Tuple, TYPE_CHECKING, Optional, Callable, Awaitable, Union

from .util import get_message_mentions
from .channel import Channel, channels
from .regex import RE_PRIVMSG, RE_WHISPER, RE_USER_JOIN, RE_USERNOTICE, RE_USER_PART, RE_NOTICE, RE_TIMEOUT_DURATION
from .enums import MessageType
from .util import split_message
from .tags import Tags
from .emote import emotes, Emote
from .config import cfg
from .util import strip_twitch_command_prefix, normalize_string, AutoCastError
from .cached_property import cached_property
from .translations import translate

if TYPE_CHECKING:
    from .irc import Irc
    from .bots import BaseBot
    from .replywaiter import ReplyResult

_TWITCH_REPLY_SPACE_REPLACEMENT = r'\s'


class Message:
    def __init__(self, msg, irc=None, bot=None):
        self.channel: Optional[Channel] = None
        self.author: Optional[str] = None
        self.content: Optional[str] = None
        self.parts: List[str] = []
        self.type: MessageType = MessageType.NONE
        self.raw_msg: str = msg
        self.receiver: Optional[str] = None
        self.irc: 'Irc' = irc
        self.tags: 'Tags' = Tags('')
        self.emotes: List[Emote] = []
        self.mentions: Tuple[str, ...] = ()
        self.system_message: Optional[str] = None
        self.bot: 'BaseBot' = bot
        self.reward: Optional[str] = None
        self.msg_id: Optional[str] = None
        self.timeout_seconds: Optional[int] = None

        self._parse()

    @classmethod
    def _handle_auto_cast(cls, value):
        if isinstance(value, Message):
            return value
        raise AutoCastError(
            reason='could not convert argument to Message, ensure that `msg` is the first argument in the function definition (after self/cls if applicable), '
                   'and no other arguments are typed as `Message`',
            send_reason_to_chat=False
        )

    def _get_channel_or_default(self, channel_name: str, default=None):
        return channels.get(channel_name, default)

    def _normalize(self, s: str):
        return s.strip().casefold()

    def _get_author(self, author: Union[str, 'Message', 'Channel']):
        if isinstance(author, Message):
            return author.author
        if isinstance(author, Channel):
            return author.name
        if author is None:
            return ''
        return normalize_string(author)

    def is_same_author(self, author: Union[str, 'Message', 'Channel']):
        return self.author is not None and self.author == self._get_author(author)

    def is_same_channel(self, author: Union[str, 'Message', 'Channel']):
        return self.author is not None and self.author == self._get_author(author)

    def is_same_author_and_channel(self, msg_or_channel: Union['Message', 'Channel']):
        return (msg_or_channel is not None
                and self.author is not None
                and self.channel is not None
                and self.author == self._get_author(msg_or_channel)
                and self.channel_name == (msg_or_channel.channel_name
                                          if isinstance(msg_or_channel, Message)
                                          else msg_or_channel.name))

    @cached_property
    def normalized_parts(self) -> Tuple[str]:
        """
        parts of the message,
        but they are are stripped of any leading or trailing whitespace
        and converted to lowercase
        """
        return tuple(map(self._normalize, self.parts))

    @cached_property
    def normalized_args(self) -> Tuple[str]:
        """
        parts of the message starting at index 1,
        but they are stripped of any leading or trailing whitespace
        and converted to lowercase
        """
        return tuple(map(self._normalize, islice(self.parts, 1, None)))

    @property
    def normalized_content(self) -> str:
        """
        lowercase()'d and strip()'d version of msg.content
        """
        return self._normalize(self.content)

    @property
    def normalized_author(self):
        return self._normalize(self.author or '')

    @property
    def args(self) -> List[str]:
        """
        parts of the message starting at index 1
        """
        return self.parts[1:]

    def _parse(self):
        # this weird looking bit is to make sure we do not do unnecessary checks when we have found a match
        # it takes advantage of the fact that python's `or` works as true check/default value provider
        # if the first check is false, it tries the next, then if thats false, it tries the next one, and it keeps doing this
        # until one matches or it run out of functions to check
        (self._parse_usernotice()
         or self._parse_notice()
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
            self.channel = self._get_channel_or_default(m['channel'])
            self.author = m['user']
            self.type = MessageType.USER_PART

        return bool(m)

    def _parse_user_join(self) -> bool:
        m = RE_USER_JOIN.search(self.raw_msg)
        if m:
            # ensure the channel exists, if it does not, create it and put it in the cache
            channel_name = m['channel']
            if channel_name not in channels:
                Channel(channel_name, irc=self.irc, register_globally=True)

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
            self.channel = self._get_channel_or_default(m['channel'])
            self.author = m['user']
            self.content = m['content']
            self.type = MessageType.PRIVMSG
            self.parts = split_message(self.content)
            self.tags = Tags(m['tags'])
            self.mentions = get_message_mentions(self)

            # checking if the message contains any bit donations
            if self.tags and self.tags.bits:
                self.type = MessageType.BITS
                # bits and rewards cannot be combined, so return here
                return True

            # checking if its a channel point redemption
            self.reward = self.tags.all_tags.get('msg-id') or self.tags.all_tags.get('custom-reward-id')
            if self.reward is not None:
                self.type = MessageType.CHANNEL_POINTS_REDEMPTION

        return bool(m)

    def _parse_usernotice(self) -> bool:
        m = RE_USERNOTICE.search(self.raw_msg)
        if m:
            self.tags = Tags(m['tags'])
            self.channel = self._get_channel_or_default(m['channel'])
            self.author = self.tags.all_tags.get('login')
            self.content = m['content']
            if self.tags.msg_id in {'sub', 'resub', 'subgift', 'anonsubgift', 'submysterygift', 'anongiftpaidupgrade',
                                    'giftpaidupgrade'}:
                self.type = MessageType.SUBSCRIPTION
            elif self.tags.msg_id == 'raid':
                self.type = MessageType.RAID
                self.author = self.tags.all_tags.get('msg-param-login')
            # RAW >> @msg-id=msg_banned :tmi.twitch.tv NOTICE #X :You are permanently banned from talking in X.
            elif self.tags.msg_id == 'msg_banned':
                self.type = MessageType.BOT_PERMANENTLY_BANNED
            elif self.tags.msg_id == 'msg_timedout':
                self.type = MessageType.BOT_TIMED_OUT
            else:
                self.type = MessageType.USER_NOTICE

        return bool(m)

    def _parse_notice(self) -> bool:
        m = RE_NOTICE.search(self.raw_msg)
        if m:
            self.tags = Tags(m['tags'])
            self.channel = self._get_channel_or_default(m['channel'])
            self.content = m['content']
            if self.tags.msg_id == 'msg_banned':
                self.type = MessageType.BOT_PERMANENTLY_BANNED
            elif self.tags.msg_id == 'msg_timedout':
                self.type = MessageType.BOT_TIMED_OUT
                self.timeout_seconds = int(RE_TIMEOUT_DURATION.search(self.content)['seconds'])
            else:
                self.type = MessageType.NOTICE

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
        return f'@{self.tags.display_name}' if self.tags.display_name else self.mention_normalized

    @property
    def mention_normalized(self):
        return f'@{self.author}' if self.author else ''

    @property
    def channel_name(self):
        if self.channel:
            return self.channel.name
        if self.author:
            return self.author
        return ''

    @property
    def has_required_tags_for_twitch_reply(self):
        tags = self.tags
        return tags is not None and all((tags.display_name, self.content is not None, tags.id, tags.user_id, self.author))

    async def send_command(self, msg: str = '', whisper=False):
        msg = f'/{strip_twitch_command_prefix(msg)}'
        await self.reply(msg=msg, whisper=whisper, strip_command_prefix=False)

    async def reply(self, msg: str = '', whisper=False, strip_command_prefix: bool = True, as_twitch_reply: bool = False):
        if not msg:
            raise ValueError('msg is empty, msg must be a non-empty string')

        twitch_message_prefix = None

        if not isinstance(msg, str):
            msg = str(msg)

        if strip_command_prefix:
            msg = strip_twitch_command_prefix(msg)

        if self.is_privmsg and as_twitch_reply and self.has_required_tags_for_twitch_reply:
            twitch_message_prefix = (f'@reply-parent-display-name={self.tags.display_name};'
                                     f'reply-parent-msg-body={self.content.replace(" ", _TWITCH_REPLY_SPACE_REPLACEMENT)};'
                                     f'reply-parent-msg-id={self.tags.id};'
                                     f'reply-parent-user-id={self.tags.user_id};'
                                     f'reply-parent-user-login={self.author}: ')

        if self.type is MessageType.PRIVMSG and (not whisper or cfg.disable_whispers):
            await self.channel.send_message(msg, _twitch_prefix=twitch_message_prefix)

        elif self.type is MessageType.WHISPER or (whisper and self.type is MessageType.PRIVMSG):
            if self.irc is None:
                raise RuntimeError('no irc instance set for this message')

            await self.irc.send_whisper(self.author, msg)

        # used for weirder cases like NOTICE, and point redemption, ect
        # exclude PRIVMSG and WHISPER since they are handled above as well
        elif self.type not in (MessageType.PRIVMSG, MessageType.WHISPER):
            # check we have a valid channel to send to
            if self.channel is not None and self.channel.irc is not None and self.channel.name.strip():
                # relay the message
                await self.channel.send_message(msg)

    TYPE_CALLABLE_PREDICATE = Union[Callable[['Message'], Awaitable[bool]], Callable[['Message'], bool]]

    async def wait_for_reply(self, predicate: TYPE_CALLABLE_PREDICATE = None, timeout=30, default=None,
                             raise_on_timeout=False) -> 'ReplyResult':
        """
        waits for a message matching `predicate` to be received, when its received, it returns that message.

        if no message matching `predicate` is received by the timeout, the default will be returned.

        if raise_on_timeout is True and no matching message is received, this function will raise asyncio.TimeoutError

        if raise_on_timeout is False and no matching message is received, default will be returned when it times-out

        default is by default is None
        raise_on_timeout by default is False
        predicate defaults to `same_author_predicate`
        """

        from .replywaiter import wait_for_reply, same_author_and_channel_predicate

        return await wait_for_reply(
            (predicate if predicate is not None else same_author_and_channel_predicate(self)),
            timeout=timeout,
            default=default,
            raise_on_timeout=raise_on_timeout
        )

    def _is_valid_arg_index(self, index: int):
        if index >= 0:
            return index < len(self.parts) - 1
        # support for negative index checks
        return -(len(self.parts) - 1) <= index <= -1

    def arg_or_default(self, index: int, default: Optional[str] = None):
        return self.args[index] if self._is_valid_arg_index(index) else default

    def has_arg_index(self, index: int):
        return self._is_valid_arg_index(index)

    def safe_print(self):
        try:
            print(self)
        except Exception as e:
            err = traceback.format_exc()
            print(err)
            with open('printing_errors.log', 'a') as f:
                f.write(f'\n\n{datetime.now()}:\n{err}')

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

        elif self.type is MessageType.BITS:
            return f'{self.author} donated {self.tags.bits} bits to #{self.channel_name}'

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
