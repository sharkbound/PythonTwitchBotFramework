from random import randint

from enums import CommandContext
from message import Message
from command import Command


@Command('roll', context=CommandContext.BOTH)
async def cmd_roll(msg: Message, *args):
    if not args:
        sides = 6
    else:
        try:
            sides = int(args[0])
        except ValueError:
            await msg.reply('invalid value for sides')
            return

    num = randint(1, sides)
    user = msg.mention if msg.is_privmsg else ''
    await msg.reply(f'{user} you rolled a {num}')
