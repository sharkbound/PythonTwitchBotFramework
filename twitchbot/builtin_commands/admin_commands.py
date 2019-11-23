import asyncio

from twitchbot import Command, CommandContext, Message, get_bot, stop_all_tasks

ADMIN_COMMAND_PERMISSION = 'admin'


@Command('shutdown', aliases=['stop', 's'], context=CommandContext.BOTH, permission=ADMIN_COMMAND_PERMISSION,
         help='make the bot shutdown')
async def cmd_shutdown(msg: Message, *args):
    await msg.reply('bot shutting down...')
    stop_all_tasks()

    for seconds_left in range(10, 0, -1):
        print(f'giving running tasks time to stop, closing in {seconds_left} seconds...')
        await asyncio.sleep(1)

    get_bot().shutdown()
