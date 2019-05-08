from twitchbot import Message, Command


@Command('ping', permission='ping')
async def cmd_debug(msg: Message, *args):
    await msg.reply('Pong!')
