from random import randint

from twitchbot import (
    Message,
    CommandContext,
    Command
)


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


@Command('crashcode', permission='crashcode')
async def cmd_crash_code(msg: Message, *args):
    await msg.reply(f'you may not crash me! {msg.mention}')
