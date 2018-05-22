from asyncio import StreamWriter, StreamReader
from .config import cfg
from .ratelimit import privmsg_ratelimit_async, whisper_ratelimit_async


class Irc:
    def __init__(self, reader, writer, bot=None):
        self.reader: StreamReader = reader
        self.writer: StreamWriter = writer

        from twitchbot.bots import BaseBot
        self.bot: BaseBot = bot

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

    @privmsg_ratelimit_async
    async def send_privmsg(self, channel: str, msg: str):
        """sends a message to a channel"""
        self.send(f'PRIVMSG #{channel} :{msg}')

        # exclude calls from send_whisper being sent to the bots on_privmsg_received event
        if self.bot and not msg.startswith('/w'):
            await self.bot.on_privmsg_sent(msg, channel, cfg.nick)

    @whisper_ratelimit_async
    async def send_whisper(self, user: str, msg: str):
        """sends a whisper to a user"""
        await self.send_privmsg(user, f'/w {user} {msg}')

        if self.bot:
            await self.bot.on_whisper_sent(msg, user, cfg.nick)

    async def get_next_message(self):
        return (await self.reader.readline()).decode().strip()

    def send_pong(self):
        self.send('PONG :tmi.twitch.tv')
