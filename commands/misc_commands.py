from channel import channels
from command import Command, commands
from enums import CommandContext
from message import Message
from database import get_all_custom_commands


@Command('list')
async def cmd_list(msg: Message, *args):
    for c in channels.values():
        await msg.reply(whisper=True,
                        msg=f'channel: {c.name}, viewers: {c.chatters.viewer_count}, is_mod: {c.is_mod}, is_live: {c.live}')


@Command('help', context=CommandContext.BOTH)
async def cmd_help(msg: Message, *args):
    custom_commands_str = ', '.join(cmd.name for cmd in get_all_custom_commands(msg.channel_name))
    global_commands_str = ', '.join(cmd.fullname for cmd in commands.values())

    await msg.reply(whisper=True, msg=f'GLOBAL: {global_commands_str}')

    if custom_commands_str:
        await msg.reply(whisper=True, msg=f'CUSTOM: {custom_commands_str}')


Command(name='commands')(cmd_help.func)


