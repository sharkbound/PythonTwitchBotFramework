from typing import List

from .config import cfg

__all__ = [
    'command_whitelist_enabled',
    'whitelisted_commands',
    'remove_command_from_whitelist',
    'add_command_to_whitelist',
    'is_command_whitelisted',
    'reload_whitelisted_commands',
    'send_message_on_command_whitelist_deny',
]


def send_message_on_command_whitelist_deny():
    return cfg.send_message_on_command_whitelist_deny


def command_whitelist_enabled() -> bool:
    return cfg.use_command_whitelist


def whitelisted_commands() -> List[str]:
    return cfg.command_whitelist


def add_command_to_whitelist(cmd_name: str, save: bool = True):
    cmd_name = cmd_name.lower()
    cmds = whitelisted_commands()
    if cmd_name not in cmds:
        cmds.append(cmd_name)
        if save:
            cfg.save()


def remove_command_from_whitelist(cmd_name: str, save: bool = True):
    cmd_name = cmd_name.lower()
    cmds = whitelisted_commands()
    if cmd_name in cmds:
        cmds.remove(cmd_name)
        if save:
            cfg.save()


def is_command_whitelisted(cmd_name: str):
    if not command_whitelist_enabled():
        return True
    return cmd_name.lower() in whitelisted_commands()


def reload_whitelisted_commands():
    cfg.load()
