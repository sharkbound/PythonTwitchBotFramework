import os
import sys
from typing import Dict, Callable
from config import cfg
from importlib import import_module
from glob import glob
from contextlib import contextmanager

from database import CustomCommand
from enums import CommandContext
from message import Message
from datetime import datetime


class Command:
    def __init__(self, name, prefix=None, func=None, global_command=True, context=CommandContext.CHANNEL):
        """
        :param name: name of the command (without the prefix)
        :param prefix: prefix require before the command name (defaults the the configs prefix if None)
        :param func: the function that the commands executes
        :param global_command: should the command be registered globally?
        :param context: the context through which calling the command is allowed
        """
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
                repl = func(msg)
                resp = resp.replace(placeholder, repl)

        await msg.channel.send_message(resp)


commands: Dict[str, Command] = {}


def load_commands_from_folder(path):
    path = os.path.abspath(path)

    if not os.path.exists(path):
        return

    with temp_syspath_append(path):
        for file in glob(os.path.join(path, '*.py')):
            fname = os.path.basename(file).split('.')[0]
            mod = import_module(fname)


@contextmanager
def temp_syspath_append(fullpath):
    sys.path.append(fullpath)
    yield
    sys.path.remove(fullpath)
