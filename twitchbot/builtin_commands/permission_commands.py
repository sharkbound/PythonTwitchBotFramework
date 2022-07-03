from twitchbot import (
    Command,
    perms,
    Message,
    cfg,
    InvalidArgumentsError,
    translate,
)

WHISPER = True

PREFIX = cfg.prefix
PERMISSION = 'manage_permissions'


@Command('addperm', permission=PERMISSION, syntax='<group> <permission>', help='adds a permission a group')
async def cmd_add_perm(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_add_perm)

    group, perm = args
    if perms.add_permission(msg.channel_name, group, perm):
        await msg.reply(whisper=WHISPER, msg=translate('addperm_added', perm=perm, group=group))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('addperm_no_group', group=group))


@Command('delperm', permission=PERMISSION, syntax='<group> <permission>', help='removes a permission from a group')
async def cmd_del_perm(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_del_perm)

    group, perm = args
    if perms.delete_permission(msg.channel_name, group, perm):
        await msg.reply(whisper=WHISPER, msg=translate('delperm_deleted', perm=perm, group=group))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('addperm_no_group', group=group))


@Command('addgroup', permission=PERMISSION, syntax='<group>', help='adds a permission group')
async def cmd_add_group(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_add_group)

    group = args[0]
    if perms.add_group(msg.channel_name, group):
        await msg.reply(whisper=WHISPER, msg=translate('addgroup_added', group=group))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('addgroup_already_exists', group=group))


@Command('delgroup', permission=PERMISSION, syntax='<group>', help='removes a permission group')
async def cmd_del_group(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_del_group)

    group = args[0]
    if perms.delete_group(msg.channel_name, group):
        await msg.reply(whisper=WHISPER, msg=translate('delgroup_deleted', group=group))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('addperm_no_group', group=group))


@Command('reloadperms', permission=PERMISSION, help='reloads permissions')
async def cmd_reload_perms(msg: Message, *args):
    if perms.reload_permissions(channel=msg.channel_name):
        await msg.reply(whisper=WHISPER, msg=translate('reloaded_permissions'))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('reloaded_permissions_failed'))


@Command('addmember', permission=PERMISSION, syntax='<group> <member>', help='adds a member to a permission group')
async def cmd_add_member(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_add_member)

    group, member = args
    member = member.lstrip('@')

    if perms.add_member(msg.channel_name, group, member):
        await msg.reply(whisper=WHISPER, msg=translate('addmember_added', member=member, group=group))
    else:
        await msg.reply(whisper=WHISPER, msg=translate('addmember_no_group'))


@Command('delmember', permission=PERMISSION, syntax='<group> <member>', help='removes a member from a permission group')
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
