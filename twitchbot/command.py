import os
import sys
from typing import Dict, Callable, Optional, List, Tuple
from .config import cfg
from importlib import import_module
from glob import glob
from contextlib import contextmanager

from twitchbot.database import CustomCommand
from .enums import CommandContext
from twitchbot.message import Message
from datetime import datetime
from .util import get_py_files, get_file_name


class Command:
    def __init__(self, name: str, prefix: str = None, func: Callable = None, global_command: bool = True,
                 context: CommandContext = CommandContext.CHANNEL, permission: str = None, syntax: str = None,
                 help: str = None):
        """
        :param name: name of the command (without the prefix)
        :param prefix: prefix require before the command name (defaults the the configs prefix if None)
        :param func: the function that the commands executes
        :param global_command: should the command be registered globally?
        :param context: the context through which calling the command is allowed
        """
        self.help: str = help
        self.syntax: str = syntax
        self.permission: str = permission
        self.context: CommandContext = context
        self.prefix: str = (prefix if prefix is not None else cfg.prefix).lower()
        self.func: Callable = func
        self.name: str = name.lower()
        self.fullname: str = self.prefix + self.name
        self.sub_cmds: Dict[str, Command] = {}
        self.parent: Command = None

        if global_command:
            commands[self.fullname] = self

    def _get_cmd_func(self, args) -> Tuple['Callable', List[str]]:
        """returns a tuple of the final commands command function and the remaining argument"""
        if not self.sub_cmds or not args or args[0].lower() not in self.sub_cmds:
            return self.func, args

        return self.sub_cmds[args[0].lower()]._get_cmd_func(args[1:])

        # while verison:
        # cmd = self
        # while cmd.sub_cmds and args and args[0].lower() in cmd.sub_cmds:
        #     cmd = cmd.sub_cmds[args[0].lower()]
        #     args = args[1:]
        #
        # return cmd.func, args

    async def execute(self, msg: Message):
        func, args = self._get_cmd_func(msg.parts[1:])
        await func(msg, *args)

    # decorator support
    def __call__(self, func) -> 'Command':
        self.func = func
        return self

    def __str__(self):
        return f'<{self.__class__.__name__} fullname={repr(self.fullname)} parent={self.parent}>'

    def __getitem__(self, item):
        return self.sub_cmds.get(item.lower()) or self.sub_cmds.get(item.lower()[1:])


class SubCommand(Command):
    def __init__(self, parent: Command, name: str, func: Callable = None, permission: str = None, syntax: str = None,
                 help: str = None):
        super().__init__(name=name, prefix='', func=func, permission=permission, syntax=syntax, help=help,
                         global_command=False)

        self.parent: Command = parent
        self.parent.sub_cmds[self.name] = self


class DummyCommand(Command):
    def __init__(self, name: str, prefix: str = None, global_command: bool = True,
                 context: CommandContext = CommandContext.CHANNEL, permission: str = None, syntax: str = None,
                 help: str = None):
        super().__init__(name=name, prefix=prefix, func=self.exec, global_command=global_command,
                         context=context, permission=permission, syntax=syntax, help=help)

    async def exec(self, msg: Message, *args):
        """the function called when the dummy command is executed"""
        if self.sub_cmds:
            await msg.reply(f'command options: {", ".join(self.sub_cmds)}')
        else:
            await msg.reply('no sub-commands were found for this command')

    def add_sub_cmd(self, name: str) -> 'DummyCommand':
        """adds a new DummyCommand to the current DummyCommand as a sub-command, then returns the new DummyCommand"""
        cmd = DummyCommand(name, prefix='', global_command=False)
        self.sub_cmds[cmd.fullname] = cmd
        return cmd


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

    async def execute(self, msg: Message):
        resp = self.cmd.response

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
        for file in get_py_files(path):
            fname = get_file_name(file)
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
