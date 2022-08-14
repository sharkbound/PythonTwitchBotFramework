from twitchbot import (
    Command,
    perms,
    Message,
    cfg,
    InvalidArgumentsError,
    translate,
    create_translate_callable,
)

WHISPER = True

PREFIX = cfg.prefix
PERMISSION = 'manage_permissions'


@Command('addperm', permission=PERMISSION, syntax='<group> <permission>', help=create_translate_callable('builtin_command_help_message_addperm'))
async def cmd_add_perm(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_add_perm)

    group, perm = args
    if perms.add_permission(msg.channel_name, group, perm):
        await msg.reply(whisper=WHISPER, msg=translate('addperm_added', perm=perm, group=group))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('addperm_no_group', group=group))


@Command('delperm', permission=PERMISSION, syntax='<group> <permission>', help=create_translate_callable('builtin_command_help_message_delperm'))
async def cmd_del_perm(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_del_perm)

    group, perm = args
    if perms.delete_permission(msg.channel_name, group, perm):
        await msg.reply(whisper=WHISPER, msg=translate('delperm_deleted', perm=perm, group=group))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('addperm_no_group', group=group))


@Command('addgroup', permission=PERMISSION, syntax='<group>', help=create_translate_callable('builtin_command_help_message_addgroup'))
async def cmd_add_group(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_add_group)

    group = args[0]
    if perms.add_group(msg.channel_name, group):
        await msg.reply(whisper=WHISPER, msg=translate('addgroup_added', group=group))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('addgroup_already_exists', group=group))


@Command('delgroup', permission=PERMISSION, syntax='<group>', help=create_translate_callable('builtin_command_help_message_delgroup'))
async def cmd_del_group(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_del_group)

    group = args[0]
    if perms.delete_group(msg.channel_name, group):
        await msg.reply(whisper=WHISPER, msg=translate('delgroup_deleted', group=group))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('addperm_no_group', group=group))


@Command('reloadperms', permission=PERMISSION, help=create_translate_callable('builtin_command_help_message_reloadperms'))
async def cmd_reload_perms(msg: Message, *args):
    if perms.reload_permissions(channel=msg.channel_name):
        await msg.reply(whisper=WHISPER, msg=translate('reloaded_permissions'))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('reloaded_permissions_failed'))


@Command('addmember', permission=PERMISSION, syntax='<group> <member>', help=create_translate_callable('builtin_command_help_message_addmember'))
async def cmd_add_member(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_add_member)

    group, member = args
    member = member.lstrip('@')

    if perms.add_member(msg.channel_name, group, member):
        await msg.reply(whisper=WHISPER, msg=translate('addmember_added', member=member, group=group))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('addmember_no_group'))


@Command('delmember', permission=PERMISSION, syntax='<group> <member>', help=create_translate_callable('builtin_command_help_message_delmember'))
async def cmd_del_member(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_del_member)

    group, member = args
    member = member.lstrip('@')

    if perms.delete_member(msg.channel_name, group, member):
        await msg.reply(whisper=WHISPER, msg=translate('delmember_deleted', member=member, group=group))
        return

    g = perms.get_group(msg.channel_name, group)
    if not g:
        await msg.reply(whisper=WHISPER,
                        msg=translate('delmember_failed_no_group'))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('delmember_member_not_in_group', member=member))
