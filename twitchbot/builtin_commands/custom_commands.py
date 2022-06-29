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
    InvalidArgumentsError,
    translate
)

PERMISSION = 'manage_commands'

PREFIX = cfg.prefix
BLACKLISTED_PREFIX_CHARACTERS = './'


def _verify_resp_is_valid(resp: str):
    return resp[0] not in BLACKLISTED_PREFIX_CHARACTERS


@Command('addcmd', permission=PERMISSION, syntax='<name> <response>',
         help='adds a custom command to the database for the this channel, '
              'placeholders: %user : the name of the person that triggered the command,'
              '%uptime : the channels live uptime,'
              '%channel : the channels name')
async def cmd_add_custom_command(msg: Message, *args):
    if len(args) < 2:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_add_custom_command)

    name, resp = args[0], ' '.join(args[1:])
    name = name.lower()

    if not _verify_resp_is_valid(resp):
        raise InvalidArgumentsError(reason=translate('add_cmd_invalid_response'),
                                    cmd=cmd_add_custom_command)

    if custom_command_exist(msg.channel_name, name):
        raise InvalidArgumentsError(reason=translate('add_cmd_duplicate'),
                                    cmd=cmd_add_custom_command)

    if add_custom_command(CustomCommand.create(msg.channel_name, name, resp)):
        await msg.reply(translate('add_cmd_success', name=name))
    else:
        await msg.reply(translate('add_cmd_fail', name=name))


@Command('updatecmd', permission=PERMISSION, syntax='<name> <response>',
         help="updates a custom command's response message")
async def cmd_update_custom_command(msg: Message, *args):
    if len(args) < 2:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_update_custom_command)

    name, resp = args[0], ' '.join(args[1:])
    name = name.lower()

    if not _verify_resp_is_valid(resp):
        raise InvalidArgumentsError(reason=translate('add_cmd_invalid_response'),
                                    cmd=cmd_update_custom_command)

    cmd = get_custom_command(msg.channel_name, name)
    if cmd is None:
        raise InvalidArgumentsError(reason=translate('update_cmd_not_exists', name=name), cmd=cmd_update_custom_command)

    cmd.response = resp
    session.commit()

    await msg.reply(translate('update_cmd_success', name=name))


@Command('delcmd', permission=PERMISSION, syntax='<name>', help='deletes a custom commands')
async def cmd_del_custom_command(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_del_custom_command)

    cmd = get_custom_command(msg.channel_name, args[0].lower())
    if cmd is None:
        raise InvalidArgumentsError(reason=translate('update_cmd_not_exists', name=args[0]), cmd=cmd_del_custom_command)

    if delete_custom_command(msg.channel_name, cmd.name):
        await msg.reply(translate('del_cmd_success', name=args[0]))
    else:
        await msg.reply(translate('del_cmd_fail', name=args[0]))


@Command('cmd', syntax='<name>', help='gets a custom commmands response')
async def cmd_get_custom_command(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_get_custom_command)

    cmd = get_custom_command(msg.channel_name, args[0].lower())
    if cmd is None:
        raise InvalidArgumentsError(reason=translate('update_cmd_not_exists', name=args[0]), cmd=cmd_get_custom_command)

    await msg.reply(translate('cmd_cmd_result', name=cmd.name, response=cmd.response))
