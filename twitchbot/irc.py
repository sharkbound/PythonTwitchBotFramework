import asyncio
import re
import typing
from asyncio import StreamWriter, StreamReader
from textwrap import wrap

from .shared import get_bot
from .config import get_nick
from .enums import Event
from .events import trigger_event
from .ratelimit import privmsg_ratelimit, whisper_ratelimit

if typing.TYPE_CHECKING:
    from .bots import BaseBot

PRIVMSG_MAX_LINE_LENGTH = 450
WHISPER_MAX_LINE_LENGTH = 438
PRIV_MSG_FORMAT = 'PRIVMSG #{channel} :{line}'


class Irc:
    def __init__(self, reader, writer):
        self.reader: StreamReader = reader
        self.writer: StreamWriter = writer
        self.bot: 'BaseBot' = get_bot()

    def send(self, msg):
        """
        sends a raw message with no modifications, this function is not ratelimited!

        do not call this function to send channel messages or whisper,
        this function is not ratelimit and intended to internal use from 'send_privmsg' and 'send_whisper'
        only use this function if you need to
        """
        self.writer.write(f'{msg}\r\n'.encode())

    def send_all(self, *msgs):
        """
        sends all messages separately with no modifications, this function is not ratelimited!

        do not call this function to send channel messages or whisper,
        this function is not ratelimit and intended to internal use from 'send_privmsg' and 'send_whisper'
        only use this function if you need to
        """
        for msg in msgs:
            self.send(msg)

    async def send_all_interval(self, *msgs, delay=.2):
        """
        sends all messages separately with no modifications, this function is not ratelimited!
        delays messages with the delay passed in from the `delay` argument

        do not call this function to send channel messages or whisper,
        this function is not ratelimit and intended to internal use from 'send_privmsg' and 'send_whisper'
        only use this function if you need to
        """
        for msg in msgs:
            self.send(msg)
            await asyncio.sleep(delay)

    async def send_privmsg(self, channel: str, msg: str):
        """sends a message to a channel"""
        # import it locally to avoid circular import
        from .channel import channels, DummyChannel
        from .modloader import trigger_mod_event

        channel = channel.lower()
        for line in _wrap_message(msg):
            await privmsg_ratelimit(channels.get(channel) or DummyChannel(channel))
            self.send(PRIV_MSG_FORMAT.format(channel=channel, line=line))

        # exclude calls from send_whisper being sent to the bots on_privmsg_received event
        if not msg.startswith('/w'):
            if self.bot:
                await self.bot.on_privmsg_sent(msg, channel, get_nick())
            await trigger_mod_event(Event.on_privmsg_sent, msg, channel, get_nick(), channel=channel)
            await trigger_event(Event.on_privmsg_sent, msg, channel, get_nick())

    async def send_whisper(self, user: str, msg: str):
        """sends a whisper to a user"""
        from .modloader import trigger_mod_event

        user = user.lower()
        for line in _wrap_message(f'/w {user} {msg}'):
            await whisper_ratelimit()
            self.send(PRIV_MSG_FORMAT.format(channel=user, line=line))
            # this sleep is necessary to make sure all whispers get sent
            # without it, consecutive whispers get dropped occasionally
            # if i find a better fix, will do it instead, but until then, this works
            await asyncio.sleep(.6)

        if self.bot:
            await self.bot.on_whisper_sent(msg, user, get_nick())
        await trigger_mod_event(Event.on_whisper_sent, msg, user, get_nick())
        await trigger_event(Event.on_whisper_sent, msg, user, get_nick())

    async def get_next_message(self):
        return (await self.reader.readline()).decode('utf8').strip()

    def send_pong(self):
        self.send('PONG :tmi.twitch.tv')


def _wrap_message(msg):
    m = re.match(r'/w (?P<user>[\w\d_]+)', msg)
    if m:
        whisper_target = m['user']
    else:
        whisper_target = None
    whisper_prefix = f'/w {whisper_target}'

    for line in wrap(msg, width=PRIVMSG_MAX_LINE_LENGTH if not msg.startswith('/w') else WHISPER_MAX_LINE_LENGTH):
        if whisper_target and not line.startswith(whisper_prefix):
            line = f'{whisper_prefix} {line}'
        yield line
