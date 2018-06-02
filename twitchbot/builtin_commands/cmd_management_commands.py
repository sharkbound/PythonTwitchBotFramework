from twitchbot import (
    Message,
    disable_command,
    enable_command,
    is_command_disabled,
    Command,
    InvalidArgumentsException,
    commands,
    get_command,
    cfg_disabled_commands
)

COMMAND_MANAGE_PERMISSION = 'manage_commands'


@Command('disablecmd',
         permission=COMMAND_MANAGE_PERMISSION,
         syntax='<name>',
         help='disables a command for the current channel')
async def cmd_disable_cmd(msg: Message, *args):
    if not args:
        raise InvalidArgumentsException()

    name = args[0].lower()

    if not get_command(name):
        return await msg.reply(f'no command found for "{name}", are you missing the prefix?')

    if is_command_disabled(msg.channel_name, name):
        return await msg.reply(f'{name} is already disabled')

    disable_command(msg.channel_name, name)

    await msg.reply(f'disabled command "{name}"')


@Command('enablecmd',
         permission=COMMAND_MANAGE_PERMISSION,
         syntax='<name>',
         help='enables a command for the current channel')
async def cmd_enable_cmd(msg: Message, *args):
    if not args:
        raise InvalidArgumentsException()

    name = args[0].lower()

    if not get_command(name):
        return await msg.reply(f'no command found for "{name}", are you missing the prefix?')

    if not is_command_disabled(msg.channel_name, name):
        return await msg.reply(f'{name} is not disabled')

    enable_command(msg.channel_name, name)

    await msg.reply(f'enabled command "{name}"')


@Command('reloaddisabled', permission=COMMAND_MANAGE_PERMISSION, help='reloads disable commands config')
async def cmd_reload_disabled(msg: Message, *args):
    cfg_disabled_commands.load()
    await msg.reply('reloaded disabled commands config')
