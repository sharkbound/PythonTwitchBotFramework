from pathlib import Path

from .config import Config
from .command import get_command, command_exist


def is_command_disabled(channel: str, cmd: str):
    cmd = get_command(cmd)
    if cmd is None:
        return False

    if channel in cfg_disabled_commands.data:
        return cmd.fullname in cfg_disabled_commands[channel]

    return False


def disable_command(channel: str, cmd: str):
    cmd = get_command(cmd)
    if cmd is None:
        return

    cmd_name = cmd.fullname
    if channel not in cfg_disabled_commands.data:
        cfg_disabled_commands[channel] = [cmd_name]
        return

    if cmd_name in cfg_disabled_commands[channel]:
        return

    cfg_disabled_commands[channel].append(cmd_name)
    cfg_disabled_commands.save()


def enable_command(channel: str, cmd: str):
    cmd = get_command(cmd)
    if cmd is None or channel not in cfg_disabled_commands.data:
        return

    if cmd.fullname in cfg_disabled_commands[channel]:
        cfg_disabled_commands[channel].remove(cmd.fullname)
        cfg_disabled_commands.save()


cfg_disabled_commands = Config(Path('configs', 'disabled_commands.json'))
