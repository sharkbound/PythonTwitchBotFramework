from twitchbot import (
    Command,
    perms,
    Message,
    cfg,
    InvalidArgumentsError)

WHISPER = True

PREFIX = cfg.prefix
PERMISSION = 'manage_permissions'


@Command('addperm', permission=PERMISSION, syntax='<group> <permission>', help='adds a permission a group')
async def cmd_add_perm(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_add_perm)

    group, perm = args
    if perms.add_permission(msg.channel_name, group, perm):
        await msg.reply(whisper=WHISPER, msg=f'added permission "{perm}" to "{group}"')
    else:
        await msg.reply(whisper=WHISPER, msg=f'no group found by the "{group}"')


@Command('delperm', permission=PERMISSION, syntax='<group> <permission>', help='removes a permission from a group')
async def cmd_del_perm(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_del_perm)

    group, perm = args
    if perms.delete_permission(msg.channel_name, group, perm):
        await msg.reply(whisper=WHISPER, msg=f'deleted permission "{perm}" from "{group}"')
    else:
        await msg.reply(whisper=WHISPER, msg=f'no group found by the "{group}"')


@Command('addgroup', permission=PERMISSION, syntax='<group>', help='adds a permission group')
async def cmd_add_group(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required argument', cmd=cmd_add_group)

    group = args[0]
    if perms.add_group(msg.channel_name, group):
        await msg.reply(whisper=WHISPER, msg=f'added permission group "{group}"')
    else:
        await msg.reply(whisper=WHISPER, msg=f'permission group "{group}" already exist')


@Command('delgroup', permission=PERMISSION, syntax='<group>', help='removes a permission group')
async def cmd_del_group(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required argument', cmd=cmd_del_group)

    group = args[0]
    if perms.delete_group(msg.channel_name, group):
        await msg.reply(whisper=WHISPER, msg=f'deleted permission group "{group}"')
    else:
        await msg.reply(whisper=WHISPER, msg=f'no group found by the "{group}"')


@Command('reloadperms', permission=PERMISSION, help='reloads permissions')
async def cmd_reload_perms(msg: Message, *args):
    if perms.reload_permissions(channel=msg.channel_name):
        await msg.reply(whisper=WHISPER, msg='reloaded permissions')
    else:
        await msg.reply(whisper=WHISPER, msg='failed to reload permissions')


@Command('addmember', permission=PERMISSION, syntax='<group> <member>', help='adds a member to a permission group')
async def cmd_add_member(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_add_member)

    group, member = args
    member = member.lstrip('@')

    if perms.add_member(msg.channel_name, group, member):
        await msg.reply(whisper=WHISPER, msg=f'added "{member}" to "{group}"')
    else:
        await msg.reply(whisper=WHISPER, msg=f'failed to add member, group does not exist')


@Command('delmember', permission=PERMISSION, syntax='<group> <member>', help='removes a member from a permission group')
async def cmd_del_member(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_del_member)

    group, member = args
    member = member.lstrip('@')

    if perms.delete_member(msg.channel_name, group, member):
        await msg.reply(whisper=WHISPER, msg=f'removed "{member}" from "{group}"')
        return

    g = perms.get_group(msg.channel_name, group)
    await msg.reply(whisper=WHISPER,
                    msg='failed to remove member, group does not exist' if not g else f'"{member}" is not in that group')
