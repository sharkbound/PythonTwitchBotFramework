from asyncio import get_event_loop
from typing import List, Optional

from .. import util
from ..channel import Channel, channels
from ..command import Command, commands, CustomCommandAction
from ..config import cfg
from ..enums import MessageType, CommandContext
from ..irc import Irc
from ..message import Message
from ..database import get_custom_command
from ..permission import perms


class BaseBot:
    def __init__(self, irc):
        self.irc: Irc = irc
        self.loop = get_event_loop()
        self.commands: List[Command] = []

    @classmethod
    async def create(cls):
        """
        this is basically a async __init__

        it creates the async reader/writer (using asyncio.open_connection())

        then returns the calls __init__ on the class and passes in the async reader/writer

        returns the created bot instance after
        """
        reader, writer = await util.get_connection()
        irc = Irc(reader, writer)
        bot = BaseBot(irc)
        irc.bot = bot

        for name in cfg.channels:
            chan = Channel(name, irc, bot)
            chan.start_update_loop()

        return bot

    def _request_permissions(self):
        # enable receiving/sending whispers
        self.irc.send('CAP REQ :twitch.tv/commands')

        # enable seeing bit donations and such
        self.irc.send('CAP REQ :twitch.tv/tags')

        # what does this even do
        # self.irc.send('CAP REQ :twitch.tv/membership')

    async def _connect(self):
        print(f'logging in as {cfg.nick}')

        util.connect(self.irc)
        self._request_permissions()

        for chan in channels.values():
            self.irc.send(f'JOIN #{chan.name}')

    async def get_command_from_msg(self, msg: Message) -> Optional[Command]:
        """
        checks if the start of the msg matches any command names

        if command is found: returns the command

        else: returns None
        """
        cmd = commands.get(msg.parts[0].lower())
        if cmd is not None:
            return cmd

        cmd = get_custom_command(msg.channel_name, msg.parts[0].lower())
        if cmd is not None:
            return CustomCommandAction(cmd)

        return None

    async def run_command(self, msg: Message, cmd: Command):
        if not self._check_permission(msg, cmd):
            await msg.reply(
                whisper=True,
                msg=f'you do not have permission to execute {cmd.fullname} in #{msg.channel_name}')
            return

        if not await self.on_before_command_execute(msg, cmd):
            return

        await cmd.func(msg, *msg.parts[1:])
        await self.on_after_command_execute(msg, cmd)

    async def on_connected(self) -> None:
        """
        triggered when the bot connects to all the channels specified in the config file
        """

    async def on_privmsg_sent(self, msg: str, channel: str, sender: str) -> None:
        """
        triggered when the bot sends a privmsg
        """
        print(f'{sender}({channel}): {msg}')

    async def on_privmsg_received(self, msg: Message) -> None:
        """triggered when a privmsg is received, is not triggered if the msg is a command"""

    async def on_whisper_sent(self, msg: str, receiver: str, sender: str):
        """
        triggered when the bot sends a whisper to someone
        """
        print(f'{cfg.nick} -> {receiver}: {msg}')

    async def on_whisper_received(self, msg: Message):
        """
        triggered when a user sends the bot a whisper
        """

    async def on_before_command_execute(self, msg: Message, cmd: Command) -> bool:
        """
        triggered before a command is executed
        :return bool, if return value is False, then the command will not be executed
        """
        return True

    async def on_after_command_execute(self, msg: Message, cmd: Command) -> None:
        """
        triggered after a command has executed
        """

    async def on_bits_donated(self, msg: Message, bits: int):
        """
        triggered when a bit donation is posted in chat
        """
        pass

    async def on_channel_joined(self, channel: Channel):
        """
        triggered when the bot joins a channel
        """
        print(f'joined #{channel.name}')

    def _check_permission(self, msg: Message, cmd: Command):
        if not cmd.permission:
            return True

        return perms.has_permission(msg.channel_name, msg.author, cmd.permission)

    async def start(self):
        await self._connect()
        await self.on_connected()

        while True:
            raw_msg = await self.irc.get_next_message()

            if not raw_msg:
                continue

            msg = Message(raw_msg, irc=self.irc, bot=self)
            coro = None
            cmd: Command = (await self.get_command_from_msg(msg)
                            if msg.is_user_message and msg.author != cfg.nick
                            else None)

            if cmd and ((msg.is_whisper and cmd.context & CommandContext.WHISPER)
                        or (msg.is_privmsg and cmd.context & CommandContext.CHANNEL)):
                coro = self.run_command(msg, cmd)

            elif msg.type is MessageType.WHISPER:
                coro = self.on_whisper_received(msg)

            elif msg.type is MessageType.PRIVMSG:
                coro = self.on_privmsg_received(msg)

            elif msg.type is MessageType.JOINED_CHANNEL:
                coro = self.on_channel_joined(msg.channel)

            elif msg.type is MessageType.PING:
                self.irc.send_pong()

            if msg.is_privmsg and msg.tags and msg.tags.bits:
                get_event_loop().create_task(self.on_bits_donated(msg, msg.tags.bits))

            if coro is not None:
                get_event_loop().create_task(coro)

            if msg.is_user_message:
                print(msg)
