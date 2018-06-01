from datetime import datetime, timedelta
from random import randint
from typing import Dict
from secrets import randbelow

from twitchbot import (
    Arena,
    ARENA_DEFAULT_ENTRY_FEE,
    Command,
    Message,
    set_currency_name,
    get_currency_name,
    set_balance,
    get_balance,
    session,
    get_balance_from_msg,
    add_balance,
    cfg,
    InvalidArgumentsException,
    Balance
)

PREFIX = cfg.prefix
PERMISSION = 'manage_currency'


@Command('setcurrencyname', permission=PERMISSION, syntax='<new_name>', help='sets the channels currency name')
async def cmd_set_currency_name(msg: Message, *args):
    if len(args) != 1:
        raise InvalidArgumentsException()

    set_currency_name(msg.channel_name, args[0])

    await msg.reply(
        f"this channel's currency name is now \"{get_currency_name(msg.channel_name).name}\"")


@Command('getcurrencyname', help='get the channels current currency name')
async def cmd_get_currency_name(msg: Message, *args):
    await msg.reply(
        f"this channel's current currency name is \"{get_currency_name(msg.channel_name).name}\"")


@Command('bal', syntax='(target)', help='gets the caller\'s (or target\'s if specified) balance')
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


@Command('setbal', permission=PERMISSION, syntax='<new_balance> (target)', help='sets the callers or targets balance')
async def cmd_set_bal(msg: Message, *args):
    if not len(args):
        raise InvalidArgumentsException()

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


@Command('give', syntax='<target> <amount>',
         help='gives the target the specified amount from the callers currency balance')
async def cmd_give(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsException()

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


@Command('gamble', syntax='<dice_sides> <bet>',
         help='throws a X sided die and if it rolls on 1 you get twice your bet + (bet*(6/<dice_sides>)), '
              'if the dice sides are more than 6 you get more payout, '
              'but it is also a lower chance to roll a 1.')
async def cmd_gamble(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsException()

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

    n = randbelow(sides) + 1
    cur_name = get_currency_name(msg.channel_name).name

    if n == 1:
        if sides >= 6:
            bet *= 2
        gain = bet + int(bet * (sides / 6))
        bal.balance += gain
        await msg.reply(f'you rolled {n} and won {gain} {cur_name}')

    else:
        bal.balance -= bet
        await msg.reply(f'you rolled {n} and lost your bet of {bet} {cur_name}')

    session.commit()


last_mine_time = {}
mine_gain = 50


@Command('mine', help='mines for currency, gives you a predefined amount (default 50)')
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


@Command('top', help="lists the top 10 balance holders")
async def cmd_top(msg: Message, *args):
    limit = 10

    results = session.query(Balance) \
        .filter(Balance.channel == msg.channel_name, Balance.user != msg.channel_name, Balance.user != cfg.nick) \
        .order_by(Balance.balance.desc()) \
        .limit(limit)

    b: Balance
    message = ', '.join(f'{i+1}: {b.user} => {b.balance}' for i, b in enumerate(results))

    await msg.reply(message or 'no balances were found')


running_arenas: Dict[str, Arena] = {}


@Command('arena', syntax='<entry_fee>',
         help='starts a arena match, waits a certain amount of time for ppl to enter, '
              'if not enough ppl enter the arena is cancelled and everyone is refunded,'
              'the winner gets all of the entry_fee\'s paid')
async def cmd_arena(msg: Message, *args):
    def _can_pay_entry_fee(fee):
        return get_balance(msg.channel_name, msg.author).balance >= fee

    arena = running_arenas.get(msg.channel_name)
    curname = get_currency_name(msg.channel_name).name

    # arena is already running for this channel
    if arena:
        if msg.author in arena.users:
            return await msg.reply(
                whisper=True,
                msg='you are already entered the in the arena')

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
    try:
        del running_arenas[arena.channel.name]
    except KeyError:
        pass
