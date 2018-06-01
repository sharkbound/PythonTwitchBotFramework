from asyncio import get_event_loop
from typing import List, Optional

from .. import util, create_irc
from ..channel import Channel, channels
from ..command import Command, commands, CustomCommandAction
from ..config import cfg
from ..enums import MessageType, CommandContext
from ..irc import Irc
from ..message import Message
from ..database import get_custom_command
from ..permission import perms
from ..emote import update_global_emotes
from ..overrides import overrides
from ..exceptions import InvalidArgumentsException


class BaseBot:
    def __init__(self):
        self.irc: Irc = None

    # region events
    @staticmethod
    async def on_connected():
        """
        triggered when the bot connects to all the channels specified in the config file
        """

    @staticmethod
    async def on_privmsg_sent(msg: str, channel: str, sender: str) -> None:
        """
        triggered when the bot sends a privmsg
        """
        print(f'{sender}({channel}): {msg}')

    @staticmethod
    async def on_privmsg_received(msg: Message) -> None:
        """triggered when a privmsg is received, is not triggered if the msg is a command"""
        print(msg)

    @staticmethod
    async def on_whisper_sent(msg: str, receiver: str, sender: str):
        """
        triggered when the bot sends a whisper to someone
        """
        print(f'{cfg.nick} -> {receiver}: {msg}')

    @staticmethod
    async def on_whisper_received(msg: Message):
        """
        triggered when a user sends the bot a whisper
        """
        print(msg)

    @staticmethod
    async def on_before_command_execute(msg: Message, cmd: Command) -> bool:
        """
        triggered before a command is executed
        :return bool, if return value is False, then the command will not be executed
        """
        return True

    @staticmethod
    async def on_after_command_execute(msg: Message, cmd: Command) -> None:
        """
        triggered after a command has executed
        """
        print(msg)

    @staticmethod
    async def on_bits_donated(msg: Message, bits: int):
        """
        triggered when a bit donation is posted in chat
        """
        pass

    @staticmethod
    async def on_channel_joined(channel: Channel):
        """
        triggered when the bot joins a channel
        """
        print(f'joined #{channel.name}')

    # endregion

    def _create_channels(self):
        for name in cfg.channels:
            chan = Channel(name, irc=self.irc, bot=self)
            chan.start_update_loop()

    async def _create_irc(self):
        """
        creates the async reader/writer (using asyncio.open_connection() if not already exist),
        """
        self.irc = await create_irc()
        self.irc.bot = self

    def _request_permissions(self):
        """requests permissions from twitch to be able to gets message tags, receive whispers, ect"""
        # enable receiving/sending whispers
        self.irc.send('CAP REQ :twitch.tv/commands')

        # enable seeing bit donations and such
        self.irc.send('CAP REQ :twitch.tv/tags')

        # what does this even do
        # self.irc.send('CAP REQ :twitch.tv/membership')

    async def _connect(self):
        """connects to twitch, sends auth info, and joins the channels in the config"""
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

    async def _run_command(self, msg: Message, cmd: Command):
        if not self._check_permission(msg, cmd):
            await msg.reply(
                whisper=True,
                msg=f'you do not have permission to execute {cmd.fullname} in #{msg.channel_name}')
            return

        if not await self.on_before_command_execute(msg, cmd):
            return

        try:
            await cmd.func(msg, *msg.parts[1:])
        except InvalidArgumentsException:
            await msg.reply(
                f'invalid args: "{cmd.fullname} {cmd.syntax}", do "{cfg.prefix}help {cmd.fullname}" for more details')
        else:
            await self.on_after_command_execute(msg, cmd)

    def _check_permission(self, msg: Message, cmd: Command):
        if not cmd.permission:
            return True

        return perms.has_permission(msg.channel_name, msg.author, cmd.permission)

    def _load_overrides(self):
        for k, v in overrides.items():
            if k.value in self.__class__.__dict__ and k.value.startswith('on'):
                setattr(self, k.value, v)

    def run(self):
        """runs/starts the bot, this is a blocking function that starts the mainloop"""
        get_event_loop().run_until_complete(self._mainloop())

    async def _mainloop(self):
        """starts the bot, loads event overrides, connects to twitch, then starts the message event loop"""
        self._load_overrides()

        await update_global_emotes()

        await self._create_irc()
        self._create_channels()

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
                coro = self._run_command(msg, cmd)

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
