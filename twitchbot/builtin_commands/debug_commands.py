from twitchbot import Message, Command, DummyCommand, SubCommand


@Command('ping')
async def cmd_debug(msg: Message, *args):
    await msg.reply('Pong!')
