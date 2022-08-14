import re
from typing import Optional
from twitchbot import (
    Message,
    InvalidArgumentsError,
    cfg,
    Command,
    get_active_channel_polls,
    get_active_channel_poll_count,
    get_channel_poll_by_id,
    PollData,
    translate,
    create_translate_callable,
)

RE_POLL_INFO = re.compile(r'(?P<title>.+)\[(?P<options>[\w\d\s,]+)]\s*(?P<time>[0-9.]*)')

VOTE_PERMISSION = 'vote'
START_POLL_PERMISSION = 'startpoll'
LIST_POLLS_PERMISSION = 'listpolls'
POLL_INFO_PERMISSION = 'pollinfo'
DEFAULT_POLL_DURATION = 60


@Command('startpoll',
         syntax='<title> [option1, option2, ect] (seconds_for_poll)',
         help=create_translate_callable('builtin_command_help_message_startpoll'),
         permission=START_POLL_PERMISSION)
async def cmd_start_poll(msg: Message, *args):
    if len(args) < 2:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_start_poll)

    poll = _parse_poll_data(msg)
    if poll is None:
        raise InvalidArgumentsError(
            reason=translate('startpoll_invalid', command_prefix=cfg.prefix),
            cmd=cmd_start_poll
        )

    await poll.start()


@Command('vote',
         syntax='<choice_id> (poll_id)',
         help=create_translate_callable('builtin_command_help_message_vote'),
         permission=VOTE_PERMISSION)
async def cmd_vote(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('vote_missing_id'), cmd=cmd_vote)

    choice = args[0]
    count = get_active_channel_poll_count(msg.channel_name)

    if not count:
        await msg.reply(translate('vote_no_active_polls'))
        return

    if count == 1:
        poll = get_active_channel_polls(msg.channel_name)[0]
    else:
        if len(args) != 2:
            await msg.reply(translate('vote_requires_id', mention=msg.mention, command_prefix=cfg.prefix, choice=choice))
            return

        passed_poll_id = _cast_to_int_or_error(args[1], cmd_vote)
        poll = get_channel_poll_by_id(msg.channel_name, passed_poll_id)

        if poll is None:
            raise InvalidArgumentsError(reason=translate('vote_poll_not_found', poll_id=passed_poll_id), cmd=cmd_vote)

    choice = _cast_to_int_or_error(choice, cmd_vote)
    if not poll.is_valid_vote(choice):
        # await msg.reply(f'{choice} is not a valid choice id for poll#{poll.id}, choices are: {poll.formatted_choices()}')
        await msg.reply(translate('vote_invalid_vote', choice=choice, poll_id=poll.id, poll_options=poll.formatted_choices()))
        return

    poll.add_vote(msg.author, choice)


@Command('listpolls', help=create_translate_callable('builtin_command_help_message_listpolls'), permission=LIST_POLLS_PERMISSION)
async def cmd_list_polls(msg: Message, *args):
    polls = get_active_channel_polls(msg.channel_name)
    if polls:
        await msg.reply(" ".join(f"{poll.id}) {poll.title}" for poll in polls))
    else:
        await msg.reply(translate('listpolls_no_polls'))


@Command('pollinfo', syntax='(POLL_ID)', help=create_translate_callable('builtin_command_help_message_pollinfo'), permission=POLL_INFO_PERMISSION)
async def cmd_poll_info(msg: Message, *args):
    count = get_active_channel_poll_count(msg.channel_name)

    if not count:
        await msg.reply(translate('pollinfo_no_polls'))
        return

    if count > 1 and not args:
        raise InvalidArgumentsError(
            reason=translate('pollinfo_requires_id', command_prefix=cfg.prefix),
            cmd=cmd_poll_info
        )

    if count == 1:
        poll = get_active_channel_polls(msg.channel_name)[0]
    else:
        poll_id = _cast_to_int_or_error(args[0], cmd_poll_info)
        poll = get_channel_poll_by_id(msg.channel_name, poll_id)

        if poll is None:
            raise InvalidArgumentsError(reason=translate('vote_poll_not_found', poll_id=poll_id), cmd=cmd_poll_info)

    await msg.reply(translate('pollinfo_result', poll_id=poll.id, poll_title=poll.title, poll_options=poll.formatted_choices(),
                              poll_seconds_left=poll.seconds_left))


def _cast_to_int_or_error(value: str, src_cmd) -> int:
    if not value.isdigit():
        raise InvalidArgumentsError(reason=translate('pollhelper_int_error', value=value), cmd=src_cmd)
    return int(value)


def _parse_poll_data(msg: Message) -> Optional[PollData]:
    match = RE_POLL_INFO.search(msg[1:])

    if not match:
        return None

    title = match[1].strip()
    choices = [s.strip() for s in match[2].split(',')]
    seconds = _try_parse_float(match[3], DEFAULT_POLL_DURATION) if len(match.groups()) == 3 else 30

    return PollData(msg.channel, msg.author, title, seconds, *choices)


def _try_parse_float(value: str, default: float) -> float:
    try:
        return float(value)
    except ValueError:
        return default
