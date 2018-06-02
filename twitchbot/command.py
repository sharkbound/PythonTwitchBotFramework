import os
import sys
from typing import Dict, Callable, Optional
from .config import cfg
from importlib import import_module
from glob import glob
from contextlib import contextmanager

from twitchbot.database import CustomCommand
from .enums import CommandContext
from twitchbot.message import Message
from datetime import datetime


class Command:
    def __init__(self, name, prefix=None, func=None, global_command=True, context=CommandContext.CHANNEL,
                 permission=None, syntax=None, help=None):
        """
        :param name: name of the command (without the prefix)
        :param prefix: prefix require before the command name (defaults the the configs prefix if None)
        :param func: the function that the commands executes
        :param global_command: should the command be registered globally?
        :param context: the context through which calling the command is allowed
        """
        self.help = help
        self.syntax = syntax
        self.permission = permission
        self.context: CommandContext = context
        self.prefix: str = (prefix if prefix is not None else cfg.prefix).lower()
        self.func: Callable = func
        self.name: str = name.lower()
        self.fullname: str = self.prefix + self.name

        if global_command:
            commands[self.fullname] = self

    # decorator support
    def __call__(self, func) -> 'Command':
        self.func = func
        return self


PLACEHOLDERS = (
    ('%user', lambda msg: f'@{msg.author}'),
    ('%uptime',
     lambda
         msg: f'{(msg.channel.stats.started_at - datetime.now()).total_seconds() / 3600:.1f}' if msg.channel.live else '[NOT LIVE]'
     ),
    ('%channel', lambda msg: msg.channel_name),
)


class CustomCommandAction(Command):
    def __init__(self, cmd):
        super().__init__(cmd.name, prefix='', func=self.execute, global_command=False)
        self.cmd: CustomCommand = cmd

    async def execute(self, msg: Message, *args):
        resp = str(self.cmd.response)

        for placeholder, func in PLACEHOLDERS:
            if placeholder in resp:
                resp = resp.replace(placeholder, func(msg))

        await msg.channel.send_message(resp)


commands: Dict[str, Command] = {}


def load_commands_from_directory(path):
    print(f'loading commands from {path}...')

    path = os.path.abspath(path)

    if not os.path.exists(path):
        return

    with temp_syspath(path):
        for file in glob(os.path.join(path, '*.py')):
            fname = os.path.basename(file).split('.')[0]
            mod = import_module(fname)


@contextmanager
def temp_syspath(fullpath):
    if fullpath not in sys.path:
        sys.path.append(fullpath)
        yield
        sys.path.remove(fullpath)
    else:
        yield


def command_exist(name: str) -> bool:
    """
    returns a bool indicating if a command exists,
    tries added a configs prefix to the name if not found initally,
    does not check for custom commands
    """
    return name in commands or (cfg.prefix + name) in commands


def get_command(name: str) -> Optional[Command]:
    """
    gets a commands,
    tries added a configs prefix to the name if not found initally,
    returns None if not exist, does not get custom commands
    """
    return commands.get(name) or commands.get(cfg.prefix + name)
