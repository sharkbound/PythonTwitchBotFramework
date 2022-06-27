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
)

MANAGE_COMMANDS_PERMISSION = 'manage_commands'


@Command('disablecmd',
         permission=MANAGE_COMMANDS_PERMISSION,
         syntax='<name>',
         help='disables a command for the current channel')
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
         help='enables a command for the current channel')
async def cmd_enable_cmd(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_enable_cmd)

    name = args[0].lower()
    if not command_exist(name):
        raise InvalidArgumentsError(reason=f'no command found for "{name}"',
                                    cmd=cmd_enable_cmd)

    if not is_command_disabled(msg.channel_name, name):
        await msg.reply(f'{name} is not disabled')
        return

    enable_command(msg.channel_name, name)
    await msg.reply(f'enabled command "{name}"')


@Command('reloaddisabled', permission=MANAGE_COMMANDS_PERMISSION, help='reloads disable commands config')
async def cmd_reload_disabled(msg: Message, *args):
    cfg_disabled_commands.load()
    await msg.reply('reloaded disabled commands config')


@Command('disablecmdglobal', permission=MANAGE_COMMANDS_PERMISSION, help='disables a command for all channels the bot is in')
async def cmd_disable_command_global(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_disable_cmd)

    cmd = args[0].lower()

    if not command_exist(cmd):
        raise InvalidArgumentsError(reason=f'no command found for "{cmd}"', cmd=cmd_disable_cmd)

    for channel in channels.values():
        disable_command(channel.name, cmd)

    await msg.reply(f'disabled command "{cmd}" globally')


@Command('enablecmdglobal',
         permission=MANAGE_COMMANDS_PERMISSION,
         syntax='<name>',
         help='enables a command for all channels the bot is in')
async def cmd_enable_command_global(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_enable_cmd)

    cmd = args[0].lower()
    if not command_exist(cmd):
        raise InvalidArgumentsError(reason=f'no command found for "{cmd}"', cmd=cmd_enable_cmd)

    for channel in channels.values():
        enable_command(channel.name, cmd)

    await msg.reply(f'enabled command "{cmd}" globally')


@Command('reloadcmdwhitelist',
         permission=MANAGE_COMMANDS_PERMISSION,
         help='reloads whitelisted commands from the config file')
async def cmd_reload_command_whitelist(msg: Message, *_):
    reload_whitelisted_commands()
    await msg.reply(f'{msg.mention} reloaded command whitelist')
