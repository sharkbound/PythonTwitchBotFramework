from twitchbot import (
    set_message_timer_active,
    set_message_timer,
    set_message_timer_interval,
    set_message_timer_message,
    restart_message_timer,
    message_timer_exist,
    delete_message_timer,
    get_all_message_timers,
    get_message_timer,
    cfg,
    Message,
    Command,
    InvalidArgumentsError,
    translate,
    create_translate_callable,
)

PREFIX = cfg.prefix
MIN_MESSAGE_TIMER_INTERVAL = 10
TIMER_PERMISSION = 'manage_timers'


async def _parse_interval(msg, value):
    try:
        interval = float(value)
        if interval < MIN_MESSAGE_TIMER_INTERVAL:
            raise ValueError()
        return True, value
    except ValueError:
        await msg.reply(translate('timer_helper_invalid_interval'))
        return False, 0


@Command('addtimer', syntax='<name> <interval> <message>', help=create_translate_callable('builtin_command_help_message_addtimer'),
         permission=TIMER_PERMISSION)
async def cmd_add_timer(msg: Message, *args):
    if len(args) < 3:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_add_timer)

    valid, interval = await _parse_interval(msg, args[1])
    if not valid:
        return

    timer_msg = ' '.join(args[2:])
    timer_name = args[0].lower()

    if message_timer_exist(msg.channel_name, timer_name):
        raise InvalidArgumentsError(reason=translate('addtimer_duplicate_name', timer_name=timer_name), cmd=cmd_add_timer)

    set_message_timer(msg.channel_name, timer_name, timer_msg, interval)
    await msg.reply(translate('addtimer_created'))


@Command('starttimer', syntax='<name>', help=create_translate_callable('builtin_command_help_message_starttimer'), permission=TIMER_PERMISSION)
async def cmd_start_timer(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(translate('missing_required_arguments'), cmd=cmd_start_timer)

    name = args[0].lower()
    timer = get_message_timer(msg.channel_name, name)

    if not timer:
        raise InvalidArgumentsError(reason=translate('starttimer_timer_not_found', name=name), cmd=cmd_start_timer)

    if timer.running:
        await msg.reply(translate('starttimer_timer_already_running', name=name))
        return

    if set_message_timer_active(msg.channel_name, name, True):
        await msg.reply(translate('starttimer_started', name=name))
    else:
        await msg.reply(translate('starttimer_failed', name=name))


@Command('stoptimer', syntax='<name>', help=create_translate_callable('builtin_command_help_message_stoptimer'), permission=TIMER_PERMISSION)
async def cmd_stop_timer(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_stop_timer)

    name = args[0].lower()
    timer = get_message_timer(msg.channel_name, name)

    if not timer:
        raise InvalidArgumentsError(reason=translate('starttimer_timer_not_found', name=name), cmd=cmd_stop_timer)

    if not timer.running:
        await msg.reply(translate('stoptimer_not_running', name=name))
        return

    if set_message_timer_active(msg.channel_name, name, False):
        await msg.reply(translate('stoptimer_stopped', name=name))
    else:
        await msg.reply(translate('stoptimer_failed', name=name))


@Command('deltimer', syntax='<name>', help=create_translate_callable('builtin_command_help_message_deltimer'), permission=TIMER_PERMISSION)
async def cmd_del_timer(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_del_timer)

    name = args[0].lower()
    timer = get_message_timer(msg.channel_name, name)

    if not timer:
        raise InvalidArgumentsError(reason=translate('starttimer_timer_not_found', name=name), cmd=cmd_del_timer)

    if delete_message_timer(msg.channel_name, name):
        await msg.reply(translate('deltimer_deleted', name=name))
    else:
        await msg.reply(translate('deltimer_failed', name=name))


@Command('listtimers', help=create_translate_callable('builtin_command_help_message_listtimers'), permission=TIMER_PERMISSION)
async def cmd_list_timers(msg: Message, *args):
    timers = get_all_message_timers(msg.channel_name)
    active_timers = ', '.join(timer.name for timer in timers if timer.active)
    inactive_timers = ', '.join(timer.name for timer in timers if not timer.active)

    if not active_timers and not inactive_timers:
        await msg.reply(translate('listtimers_no_timers'))
        return

    if active_timers:
        await msg.reply(translate('listtimers_active', active_timers=active_timers))

    if inactive_timers:
        await msg.reply(translate('listtimers_inactive', inactive_timers=inactive_timers))


@Command('edittimer', syntax='<name> <msg or interval> <new value>', help=create_translate_callable('builtin_command_help_message_edittimer'),
         permission=TIMER_PERMISSION)
async def cmd_edit_timer(msg: Message, *args):
    if len(args) < 3:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_edit_timer)

    name = args[0].lower()
    timer = get_message_timer(msg.channel_name, name)

    if not timer:
        raise InvalidArgumentsError(reason=translate('starttimer_timer_not_found', name=name), cmd=cmd_edit_timer)

    mode = args[1].lower()
    if mode not in ('msg', 'interval'):
        raise InvalidArgumentsError(reason=translate('edittimer_invalid_option'), cmd=cmd_edit_timer)

    if mode == 'interval':
        try:
            interval = int(args[2])
        except ValueError:
            raise InvalidArgumentsError(reason=translate('editimer_interval_invalid_int'), cmd=cmd_edit_timer)

        set_message_timer_interval(msg.channel_name, name, interval)
        restart_message_timer(msg.channel_name, name)

        return await msg.reply(translate('edittimer_updated_interval', name=name))

    elif mode == 'msg':
        value = ' '.join(args[2:])

        set_message_timer_message(msg.channel_name, name, value)
        restart_message_timer(msg.channel_name, name)

        return await msg.reply(translate('edittimer_updated_msg', name=name))
