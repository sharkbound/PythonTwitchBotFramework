from secrets import choice
from random import randint

from twitchbot import (
    Message,
    CommandContext,
    Command,
    cfg)


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


@Command('choose')
async def cmd_choose(msg: Message, *args):
    if len(args) < 2:
        await msg.reply(f'invalid args: {cfg.prefix}choose <option1> <option2>, ect')
        return

    await msg.reply(f'result: {choice(args)}')
