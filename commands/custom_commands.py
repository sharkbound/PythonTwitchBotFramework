import re

from command import Command
from message import Message
from database import (
    add_custom_command,
    get_custom_command,
    delete_custom_command,
    custom_command_exist,
    CustomCommand, session)
from config import cfg

PREFIX = cfg.prefix


async def _verify_resp_text(msg: Message, resp: str):
    if resp[0] in './':
        await msg.channel.send_message('responses cannot have . or / as the starting charater')
        return False

    return True


@Command('addcmd')
async def cmd_add_custom_command(msg: Message, *args):
    if len(args) < 2:
        await msg.channel.send_message(f'missing args: {PREFIX}addcmd <name> <response>')
        return

    name, resp = args[0], ' '.join(args[1:])
    name = name.lower()

    if not await _verify_resp_text(msg, resp):
        return

    if custom_command_exist(msg.channel_name, name):
        await msg.channel.send_message('custom command already exist by that name')
        return

    if add_custom_command(CustomCommand.create(msg.channel_name, name, resp)):
        await msg.channel.send_message('successfully added command')
    else:
        await msg.channel.send_message('failed to add command')


@Command('updatecmd')
async def cmd_update_custom_command(msg: Message, *args):
    if len(args) < 2:
        await msg.channel.send_message(f'missing args: {PREFIX}updatecmd <name> <response>')
        return

    name, resp = args[0], ' '.join(args[1:])
    name = name.lower()

    if not await _verify_resp_text(msg, resp):
        return

    cmd = get_custom_command(msg.channel_name, name)

    if cmd is None:
        await msg.channel.send_message(f'custom command {name} does not exist')
        return

    cmd.response = resp
    session.commit()

    await msg.channel.send_message(f'successfully updated {cmd.name}')


@Command('delcmd')
async def cmd_add_custom_command(msg: Message, *args):
    if not args:
        await msg.channel.send_message(f'missing args: {PREFIX}delcmd <name>')
        return

    cmd = get_custom_command(msg.channel_name, args[0].lower())
    if cmd is None:
        await msg.channel.send_message('no command found')
        return

    if delete_custom_command(msg.channel_name, cmd.name):
        await msg.channel.send_message(f'successfully deleted command {cmd.name}')
    else:
        await msg.channel.send_message(f'failed to delete command {cmd.name}')


@Command('getcmd')
async def cmd_get_custom_command(msg: Message, *args):
    if not args:
        await msg.channel.send_message(f'missing args: {PREFIX}getcmd <name>')
        return

    cmd = get_custom_command(msg.channel_name, args[0].lower())
    if cmd is None:
        await msg.channel.send_message('no command found')
        return

    await msg.channel.send_message(f'the response for "{cmd.name}" is "{cmd.response}"')
