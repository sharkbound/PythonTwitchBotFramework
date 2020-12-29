import asyncio
import logging
import re
import typing

import aiohttp
import websockets
import socket

from textwrap import wrap

from .shared import get_bot
from .config import get_nick, get_oauth
from .enums import Event
from .events import trigger_event
from .ratelimit import privmsg_ratelimit, whisper_ratelimit
from .shared import TWITCH_IRC_WEBSOCKET_URL, WEBSOCKET_ERRORS

PRIVMSG_MAX_LINE_LENGTH = 450
WHISPER_MAX_LINE_LENGTH = 438
PRIVMSG_FORMAT = 'PRIVMSG #{channel} :{line}'


class Irc:
    def __init__(self):
        self.socket: typing.Optional[websockets.WebSocketClientProtocol] = None

    @property
    def connected(self):
        return self.socket and self.socket.open

    async def connect_to_twitch(self):
        """
        connects to twitch and verifies is connected
        """
        print(f'logging in as {get_nick()}')
        backoff = 1

        while True:
            try:
                if not await self._create_connection():
                    raise ValueError  # used to re-trigger the reconnect code

                # send auth
                await self.send_all(f'PASS {get_oauth()}', f'NICK {get_nick()}')

                resp = (await self.get_next_message()).lower()
                if 'authentication failed' in resp:
                    print(
                        '\n\n=========AUTHENTICATION FAILED=========\n\n'
                        'check that your oauth is correct and valid and that the nick in the config is correct'
                        '\nthere is a chance that oauth was good, but is not anymore\n'
                        'the oauth token can be regenerated using this website: \n\n\thttps://twitchapps.com/tmi/')
                    input('\n\npress enter to exit')
                    exit(1)
                elif 'welcome' not in resp:
                    print(
                        f'\n\ntwitch gave a bad response to sending authentication to twitch server\nbelow is the message received from twitch:\n\n\t{resp}')
                    input('\n\npress enter to exit')
                    exit(1)

                await self.send_all('CAP REQ :twitch.tv/commands',
                                    'CAP REQ :twitch.tv/tags',  # used to get metadata from irc messages
                                    'CAP REQ :twitch.tv/membership',  # used to see user joins
                                    send_interval=.1)

                from .channel import channels
                for channel in channels.values():
                    await asyncio.sleep(.2)
                    await self.join_channel(channel.name)
            except WEBSOCKET_ERRORS:
                pass

            if not self.connected:
                logging.warning(f'[IRC_CLIENT] failed to connect to twitch... retrying in {backoff} seconds...')
                await asyncio.sleep(backoff)
                backoff <<= 1
            else:
                break

        try:
            from .emote import update_global_emotes
            from traceback import format_exc

            try:
                await update_global_emotes()
            except Exception as e:
                print(f'error trying to update emotes: {e}')
                print(f'stacktrace:\n\t{format_exc()}')

        except aiohttp.ClientConnectorError:
            logging.warning('[EMOTES API] unable to update twitch emotes list')

    async def _create_connection(self):
        try:
            self.socket = await websockets.connect(TWITCH_IRC_WEBSOCKET_URL)
            return self.connected
        except WEBSOCKET_ERRORS:
            return False

    async def send(self, msg):
        """
        sends a raw message with no modifications, this function is not ratelimited!

        do not call this function to send channel messages or whisper,
        this function is not ratelimit and intended to internal use from 'send_privmsg' and 'send_whisper'
        only use this function if you need to
        """
        await self.socket.send(f'{msg}\r\n')

    async def join_channel(self, channel_name: str):
        await self.send(f'JOIN #{channel_name}')

    async def send_all(self, *msgs, send_interval=.3):
        """
        sends all messages separately with no modifications!

        do not call this function to send channel messages or whisper,
        this function is not ratelimit and intended to internal use from 'send_privmsg' and 'send_whisper'
        only use this function if you need to
        """
        for msg in msgs:
            await self.send(msg)
            await asyncio.sleep(send_interval)  # ensure we are not sending messages too fast

    async def send_privmsg(self, channel: str, msg: str):
        """sends a message to a channel"""
        # import it locally to avoid circular import
        from .channel import channels, DummyChannel
        from .modloader import trigger_mod_event

        channel = channel.lower()
        chan = channels.get(channel) or DummyChannel(channel)
        for line in _wrap_message(msg):
            await privmsg_ratelimit(chan)
            await self.send(PRIVMSG_FORMAT.format(channel=channel, line=line))

        # exclude calls from send_whisper being sent to the bots on_privmsg_received event
        if not msg.startswith('/w'):
            if get_bot():
                await get_bot().on_privmsg_sent(msg, channel, get_nick())
            await trigger_mod_event(Event.on_privmsg_sent, msg, channel, get_nick(), channel=channel)
            await trigger_event(Event.on_privmsg_sent, msg, channel, get_nick())

    async def send_whisper(self, user: str, msg: str):
        """sends a whisper to a user"""
        from .modloader import trigger_mod_event

        user = user.lower()
        for line in _wrap_message(f'/w {user} {msg}'):
            await whisper_ratelimit()
            await self.send(PRIVMSG_FORMAT.format(channel=get_nick(), line=line))
            # this sleep is necessary to make sure all whispers get sent
            # without it, consecutive whispers get dropped occasionally
            # if i find a better fix, will do it instead, but until then, this works
            await asyncio.sleep(.6)

        if get_bot():
            await get_bot().on_whisper_sent(msg, user, get_nick())
        await trigger_mod_event(Event.on_whisper_sent, msg, user, get_nick())
        await trigger_event(Event.on_whisper_sent, msg, user, get_nick())

    async def get_next_message(self, timeout=None):
        try:
            return (await asyncio.wait_for(self.socket.recv(), timeout=timeout)).strip()
        except (websockets.ConnectionClosedError, websockets.ConnectionClosed):
            while not self.connected:
                await self.connect_to_twitch()
            return await self.get_next_message()

    async def send_pong(self):
        await self.send('PONG :tmi.twitch.tv')


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
