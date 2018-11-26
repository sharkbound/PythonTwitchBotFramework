from twitchbot import (
    set_message_timer_active,
    set_message_timer,
    set_message_timer_interval,
    set_message_timer_message,
    restart_message_timer,
    message_timer_exist,
    delete_message_timer,
    get_all_channel_timers,
    get_message_timer,
    cfg,
    Message,
    Command,
    InvalidArgumentsError
)

PREFIX = cfg.prefix
MIN_MESSAGE_TIMER_INTERVAL = 10


async def _parse_interval(msg, value):
    try:
        interval = float(value)
        if interval < MIN_MESSAGE_TIMER_INTERVAL:
            raise ValueError()
        return True, value
    except ValueError:
        await msg.reply('invalid interval, must be a valid float and be above 10')
        return False, 0


@Command('addtimer', syntax='<name> <interval> <message>', help='adds a message timer')
async def cmd_add_timer(msg: Message, *args):
    if len(args) < 3:
        raise InvalidArgumentsError

    valid, interval = await _parse_interval(msg, args[1])
    if not valid:
        return

    timer_msg = ' '.join(args[2:])
    timer_name = args[0].lower()

    if message_timer_exist(msg.channel_name, timer_name):
        await msg.reply(f'a timer already exist by the name of "{timer_name}"')
        return

    set_message_timer(msg.channel_name, timer_name, timer_msg, interval)

    await msg.reply(f'created timer successfully')


@Command('starttimer', syntax='<name>', help='starts a message timer')
async def cmd_start_timer(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError

    name = args[0].lower()
    timer = get_message_timer(msg.channel_name, name)

    if not timer:
        await msg.reply(f'no timer was found by "{name}"')
        return

    if timer.running:
        await msg.reply(f'timer "{name}" is already running')
        return

    if set_message_timer_active(msg.channel_name, name, True):
        await msg.reply(f'successfully started the timer "{name}"')
    else:
        await msg.reply(f'failed to start the timer "{name}"')


@Command('stoptimer', syntax='<name>', help='stops a message timer')
async def cmd_start_timer(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError

    name = args[0].lower()
    timer = get_message_timer(msg.channel_name, name)

    if not timer:
        await msg.reply(f'no timer was found by "{name}"')
        return

    if not timer.running:
        await msg.reply(f'that timer is not running')
        return

    if set_message_timer_active(msg.channel_name, name, False):
        await msg.reply(f'successfully stopped the timer "{name}"')
    else:
        await msg.reply(f'failed to stop the timer "{name}"')


@Command('deltimer', syntax='<name>', help='deletes a message timer')
async def cmd_del_timer(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError

    name = args[0].lower()
    timer = get_message_timer(msg.channel_name, name)

    if not timer:
        await msg.reply(f'no timer was found by "{name}"')

    if delete_message_timer(msg.channel_name, name):
        await msg.reply(f'successfully deleted timer "{name}"')
    else:
        await msg.reply(f'failed to delete timer "{name}"')


@Command('listtimers', help='lists all message timers for a channel')
async def cmd_list_timers(msg: Message, *args):
    timers = get_all_channel_timers(msg.channel_name)
    active_timers = ', '.join(timer.name for timer in timers if timer.active)
    inactive_timers = ', '.join(timer.name for timer in timers if not timer.active)

    if not active_timers and not inactive_timers:
        await msg.reply(f'no timers found for this channel')
        return

    if active_timers:
        await msg.reply(f'active timers: {active_timers}')

    if inactive_timers:
        await msg.reply(f'inactive timers: {inactive_timers}')


@Command('edittimer', syntax='<name> <msg or interval> <new value>', help="edits a timer's message or interval")
async def cmd_edit_timer(msg: Message, *args):
    if len(args) < 3:
        raise InvalidArgumentsError

    name = args[0].lower()
    timer = get_message_timer(msg.channel_name, name)

    if not timer:
        return await msg.reply(f'no timer was found by "{name}"')

    mode = args[1].lower()

    if mode not in ('msg', 'interval'):
        raise InvalidArgumentsError

    if mode == 'interval':
        try:
            interval = int(args[2])
        except ValueError:
            raise InvalidArgumentsError

        set_message_timer_interval(msg.channel_name, name, interval)
        restart_message_timer(msg.channel_name, name)

        return await msg.reply(f'updated timer interval for "{name}"')

    elif mode == 'msg':
        value = ' '.join(args[2:])

        set_message_timer_message(msg.channel_name, name, value)
        restart_message_timer(msg.channel_name, name)

        return await msg.reply(f'updated timer message for "{name}"')
