from twitchbot import Message, Command, CommandContext, SubCommand


@Command('debug', permission='debug')
async def cmd_debug(msg: Message, *args):
    await msg.reply('working')


@SubCommand(cmd_debug, 'echo')
async def cmd_debug_echo(msg: Message, *args):
    await msg.reply(' '.join(args) or 'message was empty')


@SubCommand(cmd_debug, 'name')
async def cmd_debug_echo_name(msg: Message, *args):
    await msg.reply(f'hello {msg.author}!')
