import asyncio

from twitchbot import Command, CommandContext, Message, get_bot, stop_all_tasks, translate, create_translate_callable

ADMIN_COMMAND_PERMISSION = 'admin'


@Command('shutdown', aliases=['stop'], context=CommandContext.BOTH, permission=ADMIN_COMMAND_PERMISSION,
         help=create_translate_callable('builtin_command_help_message_shutdown'))
async def cmd_shutdown(msg: Message, *args):
    await msg.reply(translate('bot_shutting_down'))
    await get_bot().shutdown()
