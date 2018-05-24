from twitchbot import Message, Command, CommandContext


@Command('debug', permission='debug')
async def cmd_debug(msg: Message, *args):
    await msg.reply(msg.raw_msg, whisper=True)
