import asyncio

from twitchbot import Command, CommandContext, Message, get_bot, stop_all_tasks

ADMIN_COMMAND_PERMISSION = 'admin'


@Command('shutdown', aliases=['stop'], context=CommandContext.BOTH, permission=ADMIN_COMMAND_PERMISSION,
         help='make the bot shutdown')
async def cmd_shutdown(msg: Message, *args):
    await msg.reply('bot shutting down...')
    await get_bot().shutdown()
