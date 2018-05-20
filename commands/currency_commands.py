import re
from datetime import datetime, timedelta
from random import randint

from command import Command
from message import Message
from database import set_currency_name, get_currency_name, set_balance, get_balance, session, get_balance_from_msg
from config import cfg

PREFIX = cfg.prefix


@Command('setcurrencyname')
async def cmd_set_currency_name(msg: Message, *args):
    if msg.author != msg.channel_name:
        await msg.reply('only the channel owner can use this command')
        return

    if len(args) != 1:
        await msg.reply(f'missing/invalid args: {PREFIX}setcurrencyname <new_name>')

    set_currency_name(msg.channel_name, args[0])

    await msg.reply(
        f"this channel's currency name is now \"{get_currency_name(msg.channel_name).name}\"")


@Command('getcurrencyname')
async def cmd_get_currency_name(msg: Message, *args):
    await msg.reply(
        f"this channel's current currency name is \"{get_currency_name(msg.channel_name).name}\"")


@Command('bal')
async def cmd_get_bal(msg: Message, *args):
    if args:
        target = args[0]
    else:
        target = msg.author

    await msg.reply(
        whisper=True,
        msg=f'@{target} has {get_balance(msg.channel_name, target).balance} '
            f'{get_currency_name(msg.channel_name).name}')


@Command('setbal')
async def cmd_set_bal(msg: Message, *args):
    if not msg.author in msg.channel.chatters.mods and msg.author != cfg.owner:
        await msg.reply('only mods can use this command')
        return

    if not len(args):
        await msg.reply(f'missing args: {PREFIX}setbal <new_balance> (user)')
        return
    elif len(args) == 2:
        target = args[1]
    else:
        target = msg.author

    try:
        set_balance(msg.channel_name, target, int(args[0]))
    except ValueError:
        await msg.reply(f'invalid target balance: {args[0]}')
        return

    await msg.reply(
        f'@{target} now has {get_balance(msg.channel_name, msg.author).balance} {get_currency_name(msg.channel_name).name}')


@Command('give')
async def cmd_give(msg: Message, *args):
    if len(args) != 2:
        await msg.reply(f'missing args: {PREFIX}give <user> <amt>')
        return

    caller = get_balance_from_msg(msg)
    target = get_balance(msg.channel_name, args[0])

    try:
        give = int(args[1])
    except ValueError:
        await msg.reply('invalid give amount')
        return

    cur_name = get_currency_name(msg.channel_name).name

    if caller.balance < give:
        await msg.reply(
            f"@{msg.author} you don't have enough {cur_name}")
        return

    caller.balance -= give
    target.balance += give

    session.commit()

    await msg.reply(
        f"@{msg.author} you gave @{args[0]} {give} {cur_name}, @{args[0]}'s balance is now {target.balance}")


@Command('gamble')
async def cmd_gamble(msg: Message, *args):
    if len(args) != 2:
        await msg.reply(
            f'USAGE: {PREFIX}gamble <dice_sides> <bet>, '
            'higher the number, the higher chance of lossing, '
            'but also gives you more when you win, '
            'you win if you roll a 1, '
            'any number less than 6 will give less than you bet')
        return

    try:
        sides = int(args[0])
        bet = int(args[1])
    except ValueError:
        await msg.reply(f'invalid value for sides or bet')
        return

    if bet < 10:
        await msg.reply('bet cannot be less then 10')
        return
    elif sides < 2:
        await msg.reply('sides cannot be less than 2')
        return

    bal = get_balance_from_msg(msg)
    if bal.balance < bet:
        await msg.reply(f"you don't have enough {get_currency_name(msg.channel_name).name}")
        return

    n = randint(1, sides)
    cur_name = get_currency_name(msg.channel_name).name

    if n == 1:
        gain = int(bet * (sides / 6))
        bal.balance += gain
        await msg.reply(f'you rolled {n} and won {gain} {cur_name}')
    else:
        bal.balance -= bet
        await msg.reply(f'you rolled {n} and lost your bet of {bet} {cur_name}')

    session.commit()


last_mine_time = {}
mine_gain = 50


@Command('mine')
async def cmd_mine(msg: Message, *args):
    key = (msg.author, msg.channel_name)
    diff = (datetime.now() - last_mine_time.get(key, datetime.now())).total_seconds()

    if key not in last_mine_time or diff >= 0:
        bal = get_balance_from_msg(msg)
        bal.balance += mine_gain
        session.commit()
        last_mine_time[key] = datetime.now() + timedelta(minutes=5)

        await msg.reply(
            f'@{msg.author} you went to work at the mines and came out with '
            f'{mine_gain} {get_currency_name(msg.channel_name).name} worth of gold',
            whisper=True)
    else:
        await msg.reply(f'you cannot mine again for {int(abs(diff))} seconds', whisper=True)


arena_running = False


@Command('arena')
async def cmd_arena(msg: Message, *args):
    pass
