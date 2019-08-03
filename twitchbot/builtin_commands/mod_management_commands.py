from twitchbot import (
    Message,
    Command,
    CommandContext,
    InvalidArgumentsError,
    is_mod_disabled,
    mod_exists,
    enable_mod,
    disable_mod,
    mods,
    reload_mod)

MOD_MANAGE_PERMISSION = 'manage_mods'


@Command('enablemod', context=CommandContext.CHANNEL, permission=MOD_MANAGE_PERMISSION,
         syntax='<mod_name>', help='enables a mod for the current channel')
async def cmd_enable_mod(msg: Message, *args):
    if len(args) != 1:
        raise InvalidArgumentsError(reason=f'expected one argument, got {len(args)}', cmd=cmd_enable_mod)

    mod = args[0]
    if not mod_exists(mod):
        raise InvalidArgumentsError(reason=f'could not find mod "{mod}"')

    if not is_mod_disabled(msg.channel_name, mod):
        await msg.reply(f'mod "{mod}" is already enabled')
        return

    enable_mod(msg.channel_name, mod)
    await msg.reply(f'mod "{mod}" has been enabled for this channel')


@Command('disablemod', context=CommandContext.CHANNEL, permission=MOD_MANAGE_PERMISSION,
         syntax='<mod_name>', help='disables a mod for the current channel')
async def cmd_disable_mod(msg: Message, *args):
    if len(args) != 1:
        raise InvalidArgumentsError(reason=f'expected one argument, got {len(args)}', cmd=cmd_disable_mod)

    mod = args[0]
    if not mod_exists(mod):
        raise InvalidArgumentsError(reason=f'could not find mod "{mod}"', cmd=cmd_disable_mod)

    if is_mod_disabled(msg.channel_name, mod):
        await msg.reply(f'mod "{mod}" is already disabled')
        return

    disable_mod(msg.channel_name, mod)
    await msg.reply(f'mod "{mod}" has been disabled for this channel')


@Command('disabledmods', context=CommandContext.CHANNEL, help='lists disabled mods for the current channel')
async def cmd_disabled_mods(msg: Message, *args):
    await msg.reply(f'disabled mods for "{msg.channel_name}": ' + ', '.join(
        mod for mod in mods if is_mod_disabled(msg.channel_name, mod)))


@Command('reloadmod', context=CommandContext.CHANNEL, syntax='<modname(case sensitive) or all>',
         permission=MOD_MANAGE_PERMISSION,
         help='reloads a specific module (case sensitive) from disk')
async def cmd_reload_mod(msg: Message, *args):
    if len(args) != 1:
        raise InvalidArgumentsError(f'missing required argument: modname', cmd=cmd_reload_mod)
    mod = args[0]

    if mod != 'all' and not mod_exists(mod):
        raise InvalidArgumentsError(f'could not find any mod by name: {mod}', cmd=cmd_reload_mod)

    if mod == 'all':
        for mod in tuple(mods):
            if not reload_mod(mod):
                await msg.reply(f'failed to reload mod "{mod}"')
                return
        await msg.reply('reloaded all mods')
        return

    if reload_mod(mod):
        await msg.reply(f'reloaded mod "{mod}"')
    else:
        await msg.reply(f'failed to reload mod "{mod}"')
