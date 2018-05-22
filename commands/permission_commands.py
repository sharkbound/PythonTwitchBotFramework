from command import Command
from permission import perms
from message import Message
from config import cfg

WHISPER = True

PREFIX = cfg.prefix
PERMISSION = 'manage_permissions'


@Command('addperm', permission=PERMISSION)
async def cmd_add_perm(msg: Message, *args):
    if len(args) != 2:
        await msg.reply(f'invalid args: {PREFIX}addperm <group> <permission>')
        return

    group, perm = args
    if perms.add_permission(msg.channel_name, group, perm):
        await msg.reply(whisper=WHISPER, msg=f'added permission "{perm}" to "{group}"')
    else:
        await msg.reply(whisper=WHISPER, msg=f'no group found by the "{group}"')


@Command('delperm', permission=PERMISSION)
async def cmd_del_perm(msg: Message, *args):
    if len(args) != 2:
        await msg.reply(f'invalid args: {PREFIX}delperm <group> <permission>')
        return

    group, perm = args
    if perms.delete_permission(msg.channel_name, group, perm):
        await msg.reply(whisper=WHISPER, msg=f'deleted permission "{perm}" from "{group}"')
    else:
        await msg.reply(whisper=WHISPER, msg=f'no group found by the "{group}"')


@Command('addgroup', permission=PERMISSION)
async def cmd_add_group(msg: Message, *args):
    if not args:
        await msg.reply(f'invalid args: {PREFIX}addgroup <group>')
        return

    group = args[0]
    if perms.add_group(msg.channel_name, group):
        await msg.reply(whisper=WHISPER, msg=f'added permission group "{group}"')
    else:
        await msg.reply(whisper=WHISPER, msg=f'permission group "{group}" already exist')


@Command('delgroup', permission=PERMISSION)
async def cmd_del_group(msg: Message, *args):
    if not args:
        await msg.reply(f'invalid args: {PREFIX}delgroup <group>')
        return

    group = args[0]
    if perms.delete_group(msg.channel_name, group):
        await msg.reply(whisper=WHISPER, msg=f'deleted permission group "{group}"')
    else:
        await msg.reply(whisper=WHISPER, msg=f'no group found by the "{group}"')


@Command('reloadperms', permission=PERMISSION)
async def cmd_reload_perms(msg: Message, *args):
    if perms.reload_permissions(channel=msg.channel_name):
        await msg.reply(whisper=WHISPER, msg='reloaded permissions')
    else:
        await msg.reply(whisper=WHISPER, msg='failed to reload permissions')


@Command('addmember', permission=PERMISSION)
async def cmd_add_member(msg: Message, *args):
    if len(args) != 2:
        await msg.reply(f'invalid args: {PREFIX}addmember <group> <member>')
        return

    group, member = args

    if member.startswith('@'):
        member = member[1:]

    if perms.add_member(msg.channel_name, group, member):
        await msg.reply(whisper=WHISPER, msg=f'added "{member}" to "{group}"')
    else:
        await msg.reply(whisper=WHISPER, msg=f'failed to add member, group does not exist')


@Command('delmember', permission=PERMISSION)
async def cmd_add_perm(msg: Message, *args):
    if len(args) != 2:
        await msg.reply(f'invalid args: {PREFIX}delmember <group> <member>')
        return

    group, member = args

    if member.startswith('@'):
        member = member[1:]

    if perms.delete_member(msg.channel_name, group, member):
        await msg.reply(whisper=WHISPER, msg=f'removed "{member}" from "{group}"')
        return

    g = perms.get_group(msg.channel_name, group)
    await msg.reply(whisper=WHISPER,
                    msg='failed to add member, group does not exist' if not g else f'"{member}" is not in that group')
