from pathlib import Path

from .config import Config
from .command import get_command, command_exist


def is_command_disabled(channel: str, cmd: str):
    if channel in cfg_disabled_commands.data:
        if command_exist(cmd):
            cmd = get_command(cmd).fullname

        return cmd in cfg_disabled_commands[channel]
    return False


def disable_command(channel: str, cmd: str):
    if channel not in cfg_disabled_commands.data:
        cfg_disabled_commands[channel] = [cmd]
        return

    if command_exist(cmd):
        cmd = get_command(cmd).fullname

    if cmd in cfg_disabled_commands[channel]:
        return

    cfg_disabled_commands[channel].append(cmd)
    cfg_disabled_commands.save()


def enable_command(channel: str, cmd: str):
    if channel not in cfg_disabled_commands.data:
        return

    if command_exist(cmd):
        cmd = get_command(cmd).fullname

    if cmd in cfg_disabled_commands[channel]:
        cfg_disabled_commands[channel].remove(cmd)
        cfg_disabled_commands.save()


cfg_disabled_commands = Config(Path('configs', 'disabled_commands.json'))
