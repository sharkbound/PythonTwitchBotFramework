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
    reload_mod,
    translate,
    create_translate_callable,
)

MOD_MANAGE_PERMISSION = 'manage_mods'


@Command('enablemod', context=CommandContext.CHANNEL, permission=MOD_MANAGE_PERMISSION,
         syntax='<mod_name>', help=create_translate_callable('builtin_command_help_message_enablemod'))
async def cmd_enable_mod(msg: Message, *args):
    if len(args) != 1:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_enable_mod)

    mod = args[0]
    if not mod_exists(mod):
        raise InvalidArgumentsError(reason=translate('enabledmod_not_found', mod=mod))

    if not is_mod_disabled(msg.channel_name, mod):
        await msg.reply(translate('enabledmod_already_enabled', mod=mod))
        return

    enable_mod(msg.channel_name, mod)
    await msg.reply(translate('enabledmod_enabled', mod=mod))


@Command('disablemod', context=CommandContext.CHANNEL, permission=MOD_MANAGE_PERMISSION,
         syntax='<mod_name>', help=create_translate_callable('builtin_command_help_message_disablemod'))
async def cmd_disable_mod(msg: Message, *args):
    if len(args) != 1:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_disable_mod)

    mod = args[0]
    if not mod_exists(mod):
        raise InvalidArgumentsError(reason=translate('enabledmod_not_found', mod=mod), cmd=cmd_disable_mod)

    if is_mod_disabled(msg.channel_name, mod):
        await msg.reply(translate('disablemod_already_disabled', mod=mod))
        return

    disable_mod(msg.channel_name, mod)
    await msg.reply(translate('disablemod_disabled', mod=mod))


@Command('disabledmods', context=CommandContext.CHANNEL, help=create_translate_callable('builtin_command_help_message_disabledmods'))
async def cmd_disabled_mods(msg: Message, *args):
    await msg.reply(translate('disabledmods_list', channel_name=msg.channel_name) + ', '.join(
        mod for mod in mods if is_mod_disabled(msg.channel_name, mod)))


@Command('reloadmod', context=CommandContext.CHANNEL, syntax='<modname(case sensitive) or all>',
         permission=MOD_MANAGE_PERMISSION,
         help=create_translate_callable('builtin_command_help_message_reloadmod'))
async def cmd_reload_mod(msg: Message, *args):
    if len(args) != 1:
        raise InvalidArgumentsError(translate('missing_required_arguments'), cmd=cmd_reload_mod)
    mod = args[0]

    if mod != 'all' and not mod_exists(mod):
        raise InvalidArgumentsError(translate('enabledmod_not_found', mod=mod), cmd=cmd_reload_mod)

    if mod == 'all':
        for mod in tuple(mods):
            if not reload_mod(mod):
                await msg.reply(translate('reloadmod_failed', mod=mod))
                return
        await msg.reply(translate('reloadmod_reloaded_all'))
        return

    if reload_mod(mod):
        await msg.reply(translate('reloadmod_success', mod=mod))
    else:
        await msg.reply(translate('reloadmod_failed', mod=mod))


@Command('listmods', context=CommandContext.CHANNEL, permission='listmods', help=create_translate_callable('builtin_command_help_message_listmods'))
async def cmd_list_mods(msg: Message, *args):
    disabled_prefix = translate('listmods_disabled_prefix')
    mods_str = ', '.join(
        f'{mod.name_or_class_name()}{disabled_prefix if is_mod_disabled(msg.channel_name, mod.name_or_class_name()) else ""}'
        for mod in mods.values()
    )
    await msg.reply(translate('listmods_found', mods=mods_str))
