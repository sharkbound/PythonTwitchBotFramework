import os
from datetime import datetime, timedelta
from itertools import count
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
    subtract_balance_from_all,
    get_nick,
    Config,
    CONFIG_FOLDER,
    SubtractBalanceResult,
    translate,
    create_translate_callable,
)

PREFIX = cfg.prefix
MANAGE_CURRENCY_PERMISSION = 'manage_currency'


@Command('setcurrencyname', permission=MANAGE_CURRENCY_PERMISSION, syntax='<new_name>',
         help=create_translate_callable('builtin_command_help_message_setcurrencyname'))
async def cmd_set_currency_name(msg: Message, *args):
    if len(args) != 1:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_set_currency_name)

    set_currency_name(msg.channel_name, args[0])
    await msg.reply(translate('currency_name_set', currency_name=get_currency_name(msg.channel_name).name))


@Command('getcurrencyname', help=create_translate_callable('builtin_command_help_message_getcurrencyname'))
async def cmd_get_currency_name(msg: Message, *ignored):
    await msg.reply(translate('currency_name_get', currency_name=get_currency_name(msg.channel_name).name))


@Command('bal', syntax='(target)', help=create_translate_callable('builtin_command_help_message_bal'))
async def cmd_get_bal(msg: Message, *args):
    if args:
        target = args[0].lstrip('@')
    else:
        target = msg.author

    currency_name = get_currency_name(msg.channel_name).name
    balance = get_balance(msg.channel_name, target).balance
    await msg.reply(translate('bal_current', target=target, balance=balance, currency_name=currency_name))


@Command('setbal', permission=MANAGE_CURRENCY_PERMISSION, syntax='<new_balance> (target)',
         help=create_translate_callable('builtin_command_help_message_setbal'))
async def cmd_set_bal(msg: Message, *args):
    if not len(args):
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_set_bal)
    elif len(args) == 2:
        target = args[1].lstrip('@')
    else:
        target = msg.author

    try:
        new_balance = int(args[0])
        if new_balance < 0:
            raise InvalidArgumentsError(reason=translate('set_bal_negative'), cmd=cmd_set_bal)

        set_balance(msg.channel_name, target, new_balance)
    except ValueError:
        raise InvalidArgumentsError(reason=translate('set_bal_invalid_int'))

    await msg.reply(translate('set_bal_success', target=target, balance=args[0], currency_name=get_currency_name(msg.channel_name).name))


@Command('addbal', permission=MANAGE_CURRENCY_PERMISSION, syntax='<user or all> <amount>',
         help=create_translate_callable('builtin_command_help_message_addbal'))
async def cmd_add_bal(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(translate('add_bal_missing_args'), cmd=cmd_add_bal)

    target = args[0].lower()
    try:
        amount = int(args[1])
    except ValueError:
        raise InvalidArgumentsError(translate('add_bal_invalid_int', value=args[1]), cmd=cmd_add_bal)

    if amount <= 0:
        raise InvalidArgumentsError(translate('add_bal_amount_must_be_positive'), cmd=cmd_add_bal)

    currency = get_currency_name(msg.channel_name).name
    if target == 'all':
        add_balance_to_all(msg.channel_name, amount)
        await msg.reply(translate('add_bal_add_all', amount=amount, currency=currency))
    else:
        add_balance(msg.channel_name, target, amount)
        await msg.reply(
            translate(
                'add_bal_success',
                target=target,
                currency=currency,
                amount=amount,
                balance=get_balance(msg.channel_name, target).balance
            )
        )


@Command('subbal', permission=MANAGE_CURRENCY_PERMISSION, syntax='<user or all> <amount>',
         help=create_translate_callable('builtin_command_help_message_subbal'))
async def cmd_sub_bal(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(translate('add_bal_missing_args'), cmd=cmd_sub_bal)

    target = args[0].lower()
    try:
        amount = int(args[1])
    except ValueError:
        raise InvalidArgumentsError(translate('add_bal_invalid_int', value=args[1]), cmd=cmd_sub_bal)

    if amount <= 0:
        raise InvalidArgumentsError(translate('add_bal_amount_must_be_positive'), cmd=cmd_sub_bal)

    currency = get_currency_name(msg.channel_name).name

    if target == 'all':
        subtract_balance_from_all(msg.channel_name, amount)
        await msg.reply(translate('sub_bal_sub_all', amount=amount, currency=currency))
        return

    result = subtract_balance(msg.channel_name, target, amount)
    if result is SubtractBalanceResult.BALANCE_DOES_NOT_EXISTS:
        raise InvalidArgumentsError(translate('sub_bal_no_balance', target=target), cmd=cmd_sub_bal)
    elif result is SubtractBalanceResult.NOT_ENOUGH_BALANCE:
        raise InvalidArgumentsError(translate('sub_bal_insufficient_balance', target=target, currency=currency, amount=amount), cmd=cmd_sub_bal)
    elif result is SubtractBalanceResult.SUCCESS:
        await msg.reply(
            translate('sub_bal_success', target=target, currency=currency, amount=amount, balance=get_balance(msg.channel_name, target).balance))


@Command('give', syntax='<target> <amount>',
         help=create_translate_callable('builtin_command_help_message_give'))
async def cmd_give(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_give)

    caller = get_balance_from_msg(msg)
    target = get_balance(msg.channel_name, args[0], create_if_missing=True)

    try:
        give = int(args[1])
    except ValueError:
        raise InvalidArgumentsError(reason=translate('give_invalid_amount_int'), cmd=cmd_give)

    if give <= 0:
        raise InvalidArgumentsError(reason=translate('give_invalid_amount_not_positive'), cmd=cmd_give)

    cur_name = get_currency_name(msg.channel_name).name

    if caller.balance < give:
        raise InvalidArgumentsError(reason=translate('give_insufficient_balance', mention=msg.mention, currency=cur_name), cmd=cmd_give)

    caller.balance -= give
    target.balance += give

    session.commit()

    target_user = args[0].strip('@')
    await msg.reply(
        translate('give_success', author=msg.author, target_user=target_user, give=give, currency=cur_name, target_balance=target.balance))


@Command('gamble', syntax='<bet> <dice_sides>',
         help=create_translate_callable('builtin_command_help_message_gamble'),
         permission='gamble')
async def cmd_gamble(msg: Message, *args):
    if not len(args):
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_gamble)

    try:
        bet = int(args[0])
    except ValueError:
        raise InvalidArgumentsError(reason=translate('gamble_invalid_bet'), cmd=cmd_gamble)

    sides = 6
    if len(args) == 2:
        if not args[1].isdigit():
            raise InvalidArgumentsError(reason=translate('gamble_invalid_dice_sides'), cmd=cmd_gamble)
        sides = int(args[1])

    if bet < 10:
        raise InvalidArgumentsError(reason=translate('gamble_bet_less_than_10'), cmd=cmd_gamble)

    elif sides < 2:
        raise InvalidArgumentsError(reason=translate('gamble_sides_less_than_2'), cmd=cmd_gamble)

    bal = get_balance_from_msg(msg)

    cur_name = get_currency_name(msg.channel_name).name
    if bal.balance < bet:
        raise InvalidArgumentsError(reason=translate('gamble_insufficient_balance', mention=msg.mention, currency=cur_name), cmd=cmd_gamble)

    def _calc_winnings(sides, roll, bet):
        if roll == sides:
            return int(bet * ((sides / 6) + 1.5))
        return int(bet * (roll / sides))

    roll = randbelow(sides) + 1
    winnings = _calc_winnings(sides=sides, roll=roll, bet=bet)

    if winnings > bet:
        gain = winnings - bet
        bal.balance += gain
        await msg.reply(translate('gamble_won', gain=gain, roll=roll, currency=cur_name))
    else:
        loss = bet - winnings
        bal.balance -= loss
        await msg.reply(translate('gamble_lost', loss=loss, roll=roll, currency=cur_name))

    session.commit()


last_mine_time = {}
mine_gain = 50


@Command('mine', help=create_translate_callable('builtin_command_help_message_mine'), permission='mine')
async def cmd_mine(msg: Message, *args):
    key = (msg.author, msg.channel_name)
    diff = (datetime.now() - last_mine_time.get(key, datetime.now())).total_seconds()

    if key not in last_mine_time or diff >= 0:
        bal = get_balance_from_msg(msg)
        bal.balance += mine_gain
        session.commit()
        last_mine_time[key] = datetime.now() + timedelta(minutes=5)

        await msg.reply(
            translate('mine_success', author=msg.author, gain=mine_gain, currency=get_currency_name(msg.channel_name).name),
            whisper=True)
    else:
        diff = int(abs(diff))
        await msg.reply(translate('mine_cooldown', diff=diff), whisper=True)


cfg_ignored_top_usernames = Config(file_path=CONFIG_FOLDER / 'command_configs' / 'command_top_config.json', ignored_usernames=[])


@Command('topreloadignored', permission='topreloadignored', help=create_translate_callable('builtin_command_help_message_topreloadignored'))
async def cmd_top_reload_ignored(msg: Message, *args):
    cfg_ignored_top_usernames.load()
    await msg.reply(translate('reloaded_top_ignored_list'))


@Command('top', help=create_translate_callable('builtin_command_help_message_top'))
async def cmd_top(msg: Message, *args):
    results = (session.query(Balance)
               .filter(Balance.channel == msg.channel_name, Balance.user != msg.channel_name,
                       Balance.user != get_nick().lower())
               .order_by(Balance.balance.desc())
               .limit(30))  # limit(30) is used to allow for some padding in-case a large number of names are filtered

    b: Balance
    counter = count(1)
    valid_matches = [
                        f'{next(counter)}: {b.user} => {b.balance}' for i, b in enumerate(results, 1)
                        if b.user.lower() not in cfg_ignored_top_usernames.ignored_usernames
                    ][:10]
    message = ' | '.join(valid_matches)

    await msg.reply(message or translate('top_no_results'))


running_arenas: Dict[str, Arena] = {}


@Command('arena', syntax='<entry_fee>',
         help=create_translate_callable('builtin_command_help_message_arena'))
async def cmd_arena(msg: Message, *args):
    def _can_pay_entry_fee(fee):
        return get_balance(msg.channel_name, msg.author).balance >= fee

    def _remove_running_arena_entry(arena: Arena):
        try:
            del running_arenas[arena.channel.name]
        except KeyError:
            pass

    Balance.ensure_exists(msg.channel_name, msg.author)
    curname = get_currency_name(msg.channel_name).name

    # arena is already running for this channel
    arena = running_arenas.get(msg.channel_name)
    if arena is not None:
        if msg.author in arena.users:
            return await msg.reply(
                whisper=True,
                msg=translate('arena_already_entered'))

        elif not _can_pay_entry_fee(arena.entry_fee):
            await msg.reply(
                whisper=True,
                msg=translate('arena_insufficient_balance', currency=curname, mention=msg.mention, entry_fee=arena.entry_fee))
            return

        arena.add_user(msg.author)
        add_balance(msg.channel_name, msg.author, -arena.entry_fee)

        await msg.reply(
            whisper=True,
            msg=translate('arena_entered', currency=curname, mention=msg.mention, entry_fee=arena.entry_fee))

    # start a new arena as one is not already running for this channel
    else:
        if args:
            try:
                entry_fee = int(args[0])
            except ValueError:
                raise InvalidArgumentsError(reason=translate('arena_invalid_entry_fee'), cmd=cmd_arena)
        else:
            entry_fee = ARENA_DEFAULT_ENTRY_FEE

        if entry_fee and entry_fee < ARENA_DEFAULT_ENTRY_FEE:
            raise InvalidArgumentsError(reason=translate('arena_entry_fee_not_high_enough', entry_fee=ARENA_DEFAULT_ENTRY_FEE), cmd=cmd_arena)

        if not _can_pay_entry_fee(entry_fee):
            await msg.reply(
                whisper=True,
                msg=translate('arena_cannot_enter_not_enough_balance', mention=msg.mention, entry_fee=entry_fee,
                              currency=curname))
            return

        arena = Arena(msg.channel, entry_fee, on_arena_ended_func=_remove_running_arena_entry)
        arena.start()
        arena.add_user(msg.author)

        subtract_balance(msg.channel_name, msg.author, arena.entry_fee)

        running_arenas[msg.channel_name] = arena


@Command('duel', syntax='<target_user> (amount, default: 10)',
         help=create_translate_callable('builtin_command_help_message_duel'))
async def cmd_duel(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_duel)

    target = args[0].lstrip('@')

    if target == msg.author:
        raise InvalidArgumentsError(reason=translate('duel_self'), cmd=cmd_duel)

    duel = get_duel(msg.channel_name, msg.author, target)

    if duel and not duel_expired(duel):
        raise InvalidArgumentsError(reason=translate('duel_duplicate', mention=msg.mention, target=target), cmd=cmd_duel)

    try:
        bet = int(args[1])
    except ValueError:
        raise InvalidArgumentsError(reason=translate('duel_invalid_bet', bet=args[1]), cmd=cmd_duel)
    except IndexError:
        bet = 10

    if bet <= 0:
        raise InvalidArgumentsError(reason=translate('duel_negative_or_zero_bet'), cmd=cmd_duel)

    caller_balance = get_balance(msg.channel_name, msg.author, create_if_missing=True)
    if caller_balance.balance < bet:
        raise InvalidArgumentsError(
            reason=translate(
                'duel_cannot_send_not_enough_balance',
                bet=bet, curname=get_currency_name(msg.channel_name).name),
            cmd=cmd_duel
        )

    target_balance = get_balance(msg.channel_name, target, create_if_missing=True)
    if target_balance is None:
        raise InvalidArgumentsError(reason=translate('duel_target_no_balance', target=target), cmd=cmd_duel)
    elif target_balance.balance < bet:
        raise InvalidArgumentsError(
            reason=translate('duel_target_insufficient_balance', target=target, currency=get_currency_name(msg.channel_name).name),
            cmd=cmd_duel
        )

    add_duel(msg.channel_name, msg.author, target, bet)

    currency_name = get_currency_name(msg.channel_name).name
    await msg.reply(translate('duel_challenged', mention=msg.mention, target=target, bet=bet, currency=currency_name, command_prefix=cfg.prefix))


@Command('accept', syntax='<challenger>', help=create_translate_callable('builtin_command_help_message_accept'))
async def cmd_accept(msg: Message, *args):
    if len(args) != 1:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'))

    challenger = args[0].lstrip('@')
    winner, bet = accept_duel(msg.channel_name, challenger, msg.author)

    if not winner:
        raise InvalidArgumentsError(
            reason=translate('duel_accept_no_duel', challenger=challenger, mention=msg.mention),
            cmd=cmd_accept)

    loser = msg.author if winner != msg.author else challenger

    add_balance(msg.channel_name, winner, bet)
    subtract_balance(msg.channel_name, loser, bet)

    currency_name = get_currency_name(msg.channel_name).name
    await msg.reply(translate('duel_accept_result', winner=winner, bet=bet, currency=currency_name))
