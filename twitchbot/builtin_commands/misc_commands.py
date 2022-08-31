from operator import attrgetter

from twitchbot import (
    Command,
    commands,
    CommandContext,
    Message, get_all_custom_commands,
    InvalidArgumentsError,
    get_command,
    is_command_disabled,
    perms,
    is_command_whitelisted,
    translate,
    create_translate_callable,
    cfg,
    get_command_chain_from_args,
)


# @Command('list')
# async def cmd_list(msg: Message, *args):
#     for c in channels.values():
#         await msg.reply(
#             whisper=True,
#             msg=f'channel: {c.name}, viewers: {c.chatters.viewer_count}, is_mod: {c.is_mod}, is_live: {c.live}')


@Command('commands', context=CommandContext.BOTH, help=create_translate_callable('builtin_command_help_message_commands'))
async def cmd_commands(msg: Message, *args):
    include_aliases = '-a' in args or '-alias' in args
    custom_commands = ', '.join(map(attrgetter('name'), get_all_custom_commands(msg.channel_name)))
    usable_commands = []
    seen = set()
    for command in commands.values():
        if (
                command.fullname in seen
                or command.hidden
                or not is_command_whitelisted(command.name)
                or is_command_disabled(msg.channel_name, command.name)
                or not perms.has_permission(msg.channel_name, msg.author, command.permission)
        ):
            continue

        seen.add(command.fullname)
        usable_commands.append(command.fullname)
        if include_aliases:
            for alias in command.aliases:
                usable_commands.append(command.prefix + alias)
    global_commands = ', '.join(usable_commands)

    if usable_commands:
        await msg.reply(whisper=True, msg=translate('commands_usable', global_commands=global_commands))
    else:
        await msg.reply(whisper=True, msg=translate('command_no_usable', mention=msg.mention))

    if custom_commands:
        await msg.reply(whisper=True, msg=translate('command_custom', custom_commands=custom_commands))


@Command(name='help', syntax='<command>', help=create_translate_callable('builtin_command_help_message_help'))
async def cmd_help(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_help)

    chain = get_command_chain_from_args(args)
    if chain is None:
        raise InvalidArgumentsError(reason=translate('command_not_found', name=args[0]), cmd=cmd_help)

    fullname = cfg.prefix + ' '.join(c.name for c in chain.chain)
    await msg.reply(msg=translate('help_success', fullname=fullname, syntax=chain.last.syntax, help=chain.last.help))


@Command(name='findperm', syntax='<command>', help=create_translate_callable('builtin_command_help_message_findperm'))
async def cmd_find_perm(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_find_perm)

    cmd = get_command(args[0])
    if not cmd:
        await msg.reply(translate('command_not_found', name=args[0]))
        return

    if not cmd.permission:
        await msg.reply(translate('findperm_no_permission', fullname=cmd.fullname))
        return

    await msg.reply(translate('findperm_success', fullname=cmd.fullname, permission=cmd.permission))
