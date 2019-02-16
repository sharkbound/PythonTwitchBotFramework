from twitchbot import (
    Message,
    disable_command,
    enable_command,
    is_command_disabled,
    Command,
    InvalidArgumentsError,
    command_exist,
    cfg_disabled_commands
)

COMMAND_MANAGE_PERMISSION = 'manage_commands'


@Command('disablecmd',
         permission=COMMAND_MANAGE_PERMISSION,
         syntax='<name>',
         help='disables a command for the current channel')
async def cmd_disable_cmd(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_disable_cmd)

    name = args[0].lower()

    if not command_exist(name):
        raise InvalidArgumentsError(reason=f'no command found for "{name}"', cmd=cmd_disable_cmd)

    if is_command_disabled(msg.channel_name, name):
        await msg.reply(f'{name} is already disabled')
        return

    disable_command(msg.channel_name, name)

    await msg.reply(f'disabled command "{name}"')


@Command('enablecmd',
         permission=COMMAND_MANAGE_PERMISSION,
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


@Command('reloaddisabled', permission=COMMAND_MANAGE_PERMISSION, help='reloads disable commands config')
async def cmd_reload_disabled(msg: Message, *args):
    cfg_disabled_commands.load()
    await msg.reply('reloaded disabled commands config')
