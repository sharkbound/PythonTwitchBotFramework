from datetime import datetime, timedelta
from secrets import randbelow
from typing import Dict

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
    InvalidArgumentsError,
    duel_expired,
    add_duel,
    accept_duel,
    subtract_balance,
    get_duel,
    add_balance_to_all,
    Balance,
    subtract_balance_from_all)

PREFIX = cfg.prefix
MANAGE_CURRENCY_PERMISSION = 'manage_currency'


@Command('setcurrencyname', permission=MANAGE_CURRENCY_PERMISSION, syntax='<new_name>',
         help='sets the channels currency name')
async def cmd_set_currency_name(msg: Message, *args):
    if len(args) != 1:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_set_currency_name)

    set_currency_name(msg.channel_name, args[0])
    await msg.reply(
        f"this channel's currency name is now \"{get_currency_name(msg.channel_name).name}\"")


@Command('getcurrencyname', help='get the channels current currency name')
async def cmd_get_currency_name(msg: Message, *ignored):
    await msg.reply(
        f'this channel\'s current currency name is "{get_currency_name(msg.channel_name).name}"')


@Command('bal', syntax='(target)', help='gets the caller\'s (or target\'s if specified) balance')
async def cmd_get_bal(msg: Message, *args):
    if args:
        target = args[0].lstrip('@')

        if target not in msg.channel.chatters:
            raise InvalidArgumentsError(reason=f'no viewer found by the name of "{target}"', cmd=cmd_get_bal)
    else:
        target = msg.author

    currency_name = get_currency_name(msg.channel_name).name
    balance = get_balance(msg.channel_name, target).balance
    await msg.reply(whisper=True, msg=f'@{target} has {balance} {currency_name}')


@Command('setbal', permission=MANAGE_CURRENCY_PERMISSION, syntax='<new_balance> (target)',
         help='sets the callers or targets balance')
async def cmd_set_bal(msg: Message, *args):
    if not len(args):
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_set_bal)
    elif len(args) == 2:
        target = args[1].lstrip('@')
        if target not in msg.channel.chatters:
            raise InvalidArgumentsError(reason=f'no viewer found by the name of "{args[1]}"', cmd=cmd_set_bal)
    else:
        target = msg.author

    try:
        new_balance = int(args[0])
        if new_balance < 0:
            raise InvalidArgumentsError(reason='new balance cannot be negative', cmd=cmd_set_bal)

        set_balance(msg.channel_name, target, new_balance)
    except ValueError:
        raise InvalidArgumentsError(reason=f'target balance must be a integer. example: 100')

    await msg.reply(
        f'@{target} now has {args[0]} '
        f'{get_currency_name(msg.channel_name).name}')


@Command('addbal', permission=MANAGE_CURRENCY_PERMISSION, syntax='<user or all> <amount>',
         help='adds the balance of the target, or all')
async def cmd_add_bal(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError('must supply both <user or all> and <amount>', cmd=cmd_add_bal)

    target = args[0].lower()
    if target != 'all' and target not in msg.channel.chatters:
        raise InvalidArgumentsError(f'cannot find any viewer named "{target}"', cmd=cmd_add_bal)

    try:
        amount = int(args[1])
    except ValueError:
        raise InvalidArgumentsError(f'cannot parse "{args[1]}" to a int, must be a valid int, ex: 100', cmd=cmd_add_bal)

    if amount <= 0:
        raise InvalidArgumentsError(f'amount must be positive and not zero, ex: 1, 2, 100', cmd=cmd_add_bal)

    currency = get_currency_name(msg.channel_name).name
    if target == 'all':
        add_balance_to_all(msg.channel_name, amount)
        await msg.reply(f"added {amount} {currency} to everyone's balance")
    else:
        add_balance(msg.channel_name, target, amount)
        await msg.reply(
            f'gave {target} {amount} {currency}, '
            f'their total is now {get_balance(msg.channel_name, target).balance} {currency}')


@Command('subbal', permission=MANAGE_CURRENCY_PERMISSION, syntax='<user or all> <amount>',
         help='subtracts the balance of the target, or all')
async def cmd_sub_bal(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError('must supply both <user or all> and <amount>', cmd=cmd_sub_bal)

    target = args[0].lower()
    if target != 'all' and target not in msg.channel.chatters:
        raise InvalidArgumentsError(f'cannot find any viewer named "{target}"', cmd=cmd_sub_bal)

    try:
        amount = int(args[1])
    except ValueError:
        raise InvalidArgumentsError(f'cannot parse "{args[1]}" to a int, must be a valid int, ex: 100', cmd=cmd_sub_bal)

    if amount <= 0:
        raise InvalidArgumentsError(f'amount must be positive and not zero, ex: 1, 2, 100', cmd=cmd_sub_bal)

    currency = get_currency_name(msg.channel_name).name

    if get_balance_from_msg(msg).balance < amount:
        raise InvalidArgumentsError(f'{target} does not have {currency} to subtract {amount} {currency} from',
                                    cmd=cmd_sub_bal)

    if target == 'all':
        subtract_balance_from_all(msg.channel_name, amount)
        await msg.reply(f"subtracted {amount} {currency} from everyone's balance")
    else:
        subtract_balance(msg.channel_name, target, amount)
        await msg.reply(
            f'subtracted {amount} {currency} from {target}, '
            f'their total is now {get_balance(msg.channel_name, target).balance} {currency}')


@Command('give', syntax='<target> <amount>',
         help='gives the target the specified amount from the callers currency balance')
async def cmd_give(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_give)

    if not msg.mentions or msg.mentions[0] not in msg.channel.chatters:
        raise InvalidArgumentsError(reason=f'no viewer found by the name "{(msg.mentions or args)[0]}"')

    caller = get_balance_from_msg(msg)
    target = get_balance(msg.channel_name, msg.mentions[0])

    try:
        give = int(args[1])
    except ValueError:
        raise InvalidArgumentsError(reason='give amount must be a integer, example: 100', cmd=cmd_give)

    if give <= 0:
        raise InvalidArgumentsError(reason='give amount must be 1 or higher', cmd=cmd_give)

    cur_name = get_currency_name(msg.channel_name).name

    if caller.balance < give:
        raise InvalidArgumentsError(reason=f"{msg.mention} you don't have enough {cur_name}", cmd=cmd_give)

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
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_gamble)

    try:
        sides = int(args[0])
        bet = int(args[1])
    except ValueError:
        raise InvalidArgumentsError(reason='invalid value for sides or bet', cmd=cmd_gamble)

    if bet < 10:
        raise InvalidArgumentsError(reason='bet cannot be less then 10', cmd=cmd_gamble)

    elif sides < 2:
        raise InvalidArgumentsError(reason='sides cannot be less than 2', cmd=cmd_gamble)

    bal = get_balance_from_msg(msg)
    cur_name = get_currency_name(msg.channel_name).name

    if bal.balance < bet:
        raise InvalidArgumentsError(reason=f"{msg.mention} you don't have enough {cur_name}", cmd=cmd_gamble)

    n = randbelow(sides) + 1

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
    results = (session.query(Balance)
               .filter(Balance.channel == msg.channel_name, Balance.user != msg.channel_name,
                       Balance.user != cfg.nick.lower())
               .order_by(Balance.balance.desc())
               .limit(10))

    b: Balance
    message = ' | '.join(f'{i}: {b.user} => {b.balance}' for i, b in enumerate(results, 1))

    await msg.reply(message or 'no users found')


running_arenas: Dict[str, Arena] = {}


@Command('arena', syntax='<entry_fee>',
         help='starts a arena match, waits a certain amount of time for ppl to enter, '
              'if not enough ppl enter the arena is cancelled and everyone is refunded,'
              'the winner gets all of the entry_fee\'s paid')
async def cmd_arena(msg: Message, *args):
    def _can_pay_entry_fee(fee):
        return get_balance(msg.channel_name, msg.author).balance >= fee

    def _remove_running_arena_entry(arena: Arena):
        try:
            del running_arenas[arena.channel.name]
        except KeyError:
            pass

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
            msg=f'{msg.mention} you have been added to the arena, '
                f'you were charged {arena.entry_fee} {curname} for entry')

    # start a new arena as one is not already running for this channel
    else:
        if args:
            try:
                entry_fee = int(args[0])
            except ValueError:
                raise InvalidArgumentsError(reason='invalid value for entry fee, example: 100', cmd=cmd_arena)
        else:
            entry_fee = ARENA_DEFAULT_ENTRY_FEE

        if entry_fee and entry_fee < ARENA_DEFAULT_ENTRY_FEE:
            raise InvalidArgumentsError(reason=f'entry fee cannot be less than {ARENA_DEFAULT_ENTRY_FEE}',
                                        cmd=cmd_arena)

        if not _can_pay_entry_fee(entry_fee):
            await msg.reply(
                whisper=True,
                msg=f'{msg.mention} you do not have {entry_fee} {curname}')
            return

        arena = Arena(msg.channel, entry_fee, on_arena_ended_func=_remove_running_arena_entry)
        arena.start()
        arena.add_user(msg.author)

        subtract_balance(msg.channel_name, msg.author, arena.entry_fee)

        running_arenas[msg.channel_name] = arena


@Command('duel', syntax='<target_user> (amount, default: 10)',
         help='challenges a user to a duel with the bid as the reward')
async def cmd_duel(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_duel)

    target = args[0].lstrip('@')

    if target == msg.author:
        raise InvalidArgumentsError(reason='you cannot duel yourself', cmd=cmd_duel)

    if target not in msg.channel.chatters:
        raise InvalidArgumentsError(reason=f'{msg.mention} {target} is not in this channel', cmd=cmd_duel)

    duel = get_duel(msg.channel_name, msg.author, target)

    if duel and not duel_expired(duel):
        raise InvalidArgumentsError(reason=f'{msg.mention} you already have a pending duel with {target}', cmd=cmd_duel)

    try:
        bet = int(args[1])
    except ValueError:
        raise InvalidArgumentsError(reason=f'invalid bet: {args[1]}, bet must be a number with no decimals, ex: 12',
                                    cmd=cmd_duel)
    except IndexError:
        bet = 10

    add_duel(msg.channel_name, msg.author, target, bet)

    currency_name = get_currency_name(msg.channel_name).name
    await msg.reply(
        f'{msg.mention} has challenged @{target} to a duel for {bet} {currency_name}'
        f', do "{cfg.prefix}accept {msg.mention}" to accept the duel')


@Command('accept', syntax='<challenger>', help='accepts a duel issued by the challenger that is passed to this command')
async def cmd_accept(msg: Message, *args):
    if len(args) != 1:
        raise InvalidArgumentsError('missing required arguments')

    challenger = args[0].lstrip('@')
    winner, bet = accept_duel(msg.channel_name, challenger, msg.author)

    if not winner:
        raise InvalidArgumentsError(
            reason=f'{msg.mention}, you have not been challenged by {challenger}, or the duel might have expired',
            cmd=cmd_accept)

    loser = msg.author if winner == msg.author else challenger

    add_balance(msg.channel_name, winner, bet)
    subtract_balance(msg.channel_name, loser, bet)

    currency_name = get_currency_name(msg.channel_name).name
    await msg.reply(f'@{winner} has won the duel, {bet} {currency_name} went to the winner')
