from twitchbot import (
    Message,
    add_custom_command,
    get_custom_command,
    delete_custom_command,
    custom_command_exist,
    CustomCommand,
    session,
    cfg,
    Command,
    InvalidArgumentsError)

PERMISSION = 'manange_commands'

PREFIX = cfg.prefix


async def _verify_resp_text(msg: Message, resp: str):
    if resp[0] in './':
        await msg.reply(msg='responses cannot have . or / as the starting charater')
        return False

    return True


@Command('addcmd', permission=PERMISSION, syntax='<name> <response>',
         help='adds a custom command to the database for the this channel.'
              'place holders: %user : the name of the person that triggered the command,'
              '%uptime : the channels live uptime,'
              '%channel : the channels name')
async def cmd_add_custom_command(msg: Message, *args):
    if len(args) < 2:
        raise InvalidArgumentsError

    name, resp = args[0], ' '.join(args[1:])
    name = name.lower()

    if not await _verify_resp_text(msg, resp):
        return

    if custom_command_exist(msg.channel_name, name):
        await msg.reply('custom command already exist by that name')
        return

    if add_custom_command(CustomCommand.create(msg.channel_name, name, resp)):
        await msg.reply('successfully added command')
    else:
        await msg.reply('failed to add command')


@Command('updatecmd', permission=PERMISSION, syntax='<name> <response>',
         help="updates a custom command's response message")
async def cmd_update_custom_command(msg: Message, *args):
    if len(args) < 2:
        raise InvalidArgumentsError

    name, resp = args[0], ' '.join(args[1:])
    name = name.lower()

    if not await _verify_resp_text(msg, resp):
        return

    cmd = get_custom_command(msg.channel_name, name)

    if cmd is None:
        await msg.reply(f'custom command {name} does not exist')
        return

    cmd.response = resp
    session.commit()

    await msg.reply(f'successfully updated {cmd.name}')


@Command('delcmd', permission=PERMISSION, syntax='<name>', help='deletes a custom commands')
async def cmd_add_custom_command(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError

    cmd = get_custom_command(msg.channel_name, args[0].lower())
    if cmd is None:
        await msg.reply('no command found')
        return

    if delete_custom_command(msg.channel_name, cmd.name):
        await msg.reply(f'successfully deleted command {cmd.name}')
    else:
        await msg.reply(f'failed to delete command {cmd.name}')


@Command('cmd', syntax='<name>', help='gets a custom commmands response')
async def cmd_get_custom_command(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError

    cmd = get_custom_command(msg.channel_name, args[0].lower())
    if cmd is None:
        await msg.reply('no command found')
        return

    await msg.reply(f'the response for "{cmd.name}" is "{cmd.response}"')
