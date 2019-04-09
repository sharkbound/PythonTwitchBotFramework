from twitchbot import Command, CommandContext, Message

ADMIN_COMMAND_PERMISSION = 'admin'


@Command('shutdown', context=CommandContext.BOTH, permission=ADMIN_COMMAND_PERMISSION,
         help='make the bot shutdown')
async def cmd_restart(msg: Message, *args):
    await msg.reply('bot shutting down...')
    msg.bot.shutdown()
