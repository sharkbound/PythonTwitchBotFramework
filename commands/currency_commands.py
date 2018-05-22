from datetime import datetime, timedelta
from random import randint
from typing import Dict

from arena import Arena, ARENA_DEFAULT_ENTRY_FEE
from command import Command
from message import Message
from database import set_currency_name, get_currency_name, set_balance, get_balance, session, get_balance_from_msg, \
    add_balance
from config import cfg

PREFIX = cfg.prefix
PERMISSION = 'manage_currency'


@Command('setcurrencyname', permission=PERMISSION)
async def cmd_set_currency_name(msg: Message, *args):
    if msg.author not in (msg.channel_name, cfg.owner):
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

        if target not in msg.channel.chatters:
            await msg.reply(msg=f'no viewer found by the name of "{target}"')
            return
    else:
        target = msg.author

    await msg.reply(
        whisper=True,
        msg=f'@{target} has {get_balance(msg.channel_name, target).balance} '
            f'{get_currency_name(msg.channel_name).name}')


@Command('setbal', permission=PERMISSION)
async def cmd_set_bal(msg: Message, *args):
    if not len(args):
        await msg.reply(f'invalid args: {PREFIX}setbal <new_balance> (user)')
        return
    elif len(args) == 2:
        target = args[1]

        if target not in msg.channel.chatters:
            await msg.reply(msg=f'no viewer found by the name of "{args[1]}"')
            return
    else:
        target = msg.author

    try:
        set_balance(msg.channel_name, target, int(args[0]))
    except ValueError:
        await msg.reply(f'invalid target balance: {args[0]}')
        return

    await msg.reply(
        f'@{target} now has {args[0]} '
        f'{get_currency_name(msg.channel_name).name}')


@Command('give')
async def cmd_give(msg: Message, *args):
    if len(args) != 2:
        await msg.reply(f'invalid args: {PREFIX}give <user> <amt>')
        return

    if args[0] not in msg.channel.chatters:
        await msg.reply(msg=f'no viewer found by the name "{args[0]}"')
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


running_arenas: Dict[str, Arena] = {}


@Command('arena')
async def cmd_arena(msg: Message, *args):
    def _can_pay_entry_fee(fee):
        return get_balance(msg.channel_name, msg.author).balance >= fee

    arena = running_arenas.get(msg.channel_name)
    curname = get_currency_name(msg.channel_name).name

    # arena is already running for this channel
    if arena:
        if msg.author in arena.users:
            await msg.reply(
                whisper=True,
                msg='you are already entered the in the arena')
            return

        elif not _can_pay_entry_fee(arena.entry_fee):
            await msg.reply(
                whisper=True,
                msg=f'{msg.mention} you do not have enough {curname} '
                    f'to join the arena, entry_fee is {arena.entry_fee} {curname}')
            return

        arena.add_user(msg.author)
        add_balance(msg.channel_name, msg.author, -arena.entry_fee)

        await msg.reply(
            whisper=True,
            msg=f'{msg.mention} you have been added to the arena, you were charged {arena.entry_fee} {curname} upon entry')

    # start a new arena as one is not already running for this channel
    else:
        if args:
            try:
                entry_fee = int(args[0])
            except ValueError:
                await msg.reply(msg='invalid value for entry fee')
                return
        else:
            entry_fee = ARENA_DEFAULT_ENTRY_FEE

        if entry_fee and entry_fee < ARENA_DEFAULT_ENTRY_FEE:
            await msg.reply(msg=f'entry fee cannot be less than {ARENA_DEFAULT_ENTRY_FEE}')
            return

        if not _can_pay_entry_fee(entry_fee):
            await msg.reply(
                whisper=True,
                msg=f'{msg.mention} you do not have {entry_fee} {curname}')
            return

        arena = Arena(msg.channel, entry_fee, on_arena_ended_func=_remove_running_arena_entry)
        arena.start()
        arena.add_user(msg.author)

        add_balance(msg.channel_name, msg.author, -arena.entry_fee)

        running_arenas[msg.channel_name] = arena


def _remove_running_arena_entry(arena: Arena):
    global running_arenas

    try:
        del running_arenas[arena.channel.name]
        print('success')
    except:
        pass
