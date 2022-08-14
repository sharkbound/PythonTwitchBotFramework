from twitchbot import (
    Message,
    disable_command,
    enable_command,
    is_command_disabled,
    Command,
    InvalidArgumentsError,
    command_exist,
    cfg_disabled_commands,
    channels,
    reload_whitelisted_commands,
    translate,
    create_translate_callable,
)

MANAGE_COMMANDS_PERMISSION = 'manage_commands'


@Command('disablecmd',
         permission=MANAGE_COMMANDS_PERMISSION,
         syntax='<name>',
         help=create_translate_callable('builtin_command_help_message_disablecmd'))
async def cmd_disable_cmd(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_disable_cmd)

    name = args[0].lower()

    if not command_exist(name):
        raise InvalidArgumentsError(reason=translate('command_not_found', name=name), cmd=cmd_disable_cmd)

    if is_command_disabled(msg.channel_name, name):
        await msg.reply(translate('command_already_disabled', name=name))
        return

    disable_command(msg.channel_name, name)

    await msg.reply(translate('disabled_command', name=name))


@Command('enablecmd',
         permission=MANAGE_COMMANDS_PERMISSION,
         syntax='<name>',
         help=create_translate_callable('builtin_command_help_message_enablecmd'))
async def cmd_enable_cmd(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_enable_cmd)

    name = args[0].lower()
    if not command_exist(name):
        raise InvalidArgumentsError(reason=translate('command_not_found', name=name),
                                    cmd=cmd_enable_cmd)

    if not is_command_disabled(msg.channel_name, name):
        await msg.reply(translate('command_not_disabled', name=name))
        return

    enable_command(msg.channel_name, name)
    await msg.reply(translate('command_enabled', name=name))


@Command('reloaddisabled', permission=MANAGE_COMMANDS_PERMISSION, help=create_translate_callable('builtin_command_help_message_reloaddisabled'))
async def cmd_reload_disabled(msg: Message, *args):
    cfg_disabled_commands.load()
    await msg.reply(translate('reloaded_disabled_commands_config', user=msg.author))


@Command('disablecmdglobal', permission=MANAGE_COMMANDS_PERMISSION, help=create_translate_callable('builtin_command_help_message_disablecmdglobal'))
async def cmd_disable_command_global(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_disable_cmd)

    cmd = args[0].lower()

    if not command_exist(cmd):
        raise InvalidArgumentsError(reason=translate('command_not_found', name=cmd), cmd=cmd_disable_cmd)

    for channel in channels.values():
        disable_command(channel.name, cmd)

    await msg.reply(translate('disabled_command_globally', name=cmd))


@Command('enablecmdglobal',
         permission=MANAGE_COMMANDS_PERMISSION,
         syntax='<name>',
         help=create_translate_callable('builtin_command_help_message_enablecmdglobal'))
async def cmd_enable_command_global(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_enable_cmd)

    cmd = args[0].lower()
    if not command_exist(cmd):
        raise InvalidArgumentsError(reason=translate('command_not_found', name=cmd), cmd=cmd_enable_cmd)

    for channel in channels.values():
        enable_command(channel.name, cmd)

    await msg.reply(translate('enabled_command_globally', name=cmd))


@Command('reloadcmdwhitelist',
         permission=MANAGE_COMMANDS_PERMISSION,
         help=create_translate_callable('builtin_command_help_message_reloadcmdwhitelist'))
async def cmd_reload_command_whitelist(msg: Message, *_):
    reload_whitelisted_commands()
    await msg.reply(translate('reloaded_command_whitelist', mention=msg.mention))
