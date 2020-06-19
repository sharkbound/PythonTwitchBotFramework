from twitchbot import *

RE_POLL_INFO = re.compile(r'(?P<title>.+)\[(?P<options>[\w\d\s,]+)]\s*(?P<time>[0-9.]*)')

VOTE_PERMISSION = 'vote'
START_POLL_PERMISSION = 'startpoll'
LIST_POLLS_PERMISSION = 'listpolls'
POLL_INFO_PERMISSION = 'pollinfo'
DEFAULT_POLL_DURATION = 60


@Command('startpoll',
         syntax='<title> [option1, option2, ect] (seconds_for_poll)',
         help='starts the poll for the the current channel',
         permission=START_POLL_PERMISSION)
async def cmd_start_poll(msg: Message, *args):
    if len(args) < 2:
        raise InvalidArgumentsError(reason='missing required poll arguments', cmd=cmd_start_poll)

    poll = _parse_poll_data(msg)
    if poll is None:
        raise InvalidArgumentsError(
            reason=f'your poll commands seems to be improperly formatted, example: {cfg.prefix}startpoll what should i eat? [apples, oranges, potatos]',
            cmd=cmd_start_poll
        )

    await poll.start()


@Command('vote',
         syntax='<choice_id> (poll_id)',
         help='starts the poll for the the current channel',
         permission=VOTE_PERMISSION)
async def cmd_vote(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required vote arguments, must provide the id of the choice you want to vote for', cmd=cmd_vote)

    choice = args[0]
    count = get_active_channel_poll_count(msg.channel_name)

    if not count:
        await msg.reply('there are NOT any active polls running right now to vote for')
        return

    if count == 1:
        poll = get_active_channel_polls(msg.channel_name)[0]
    else:
        if len(args) != 2:
            await msg.reply(
                f'{msg.mention} there are multiple polls active, please specify the poll id, example: {cfg.prefix}vote {choice} <POLL_ID>')
            return

        passed_poll_id = _cast_to_int_or_error(args[1], cmd_vote)
        poll = get_channel_poll_by_id(msg.channel_name, passed_poll_id)

        if poll is None:
            raise InvalidArgumentsError(reason=f'Could not find poll by ID {passed_poll_id}', cmd=cmd_vote)

    choice = _cast_to_int_or_error(choice, cmd_vote)
    if not poll.is_valid_vote(choice):
        await msg.reply(f'{choice} is not a valid choice id for poll#{poll.id}, choices are: {poll.format_choices()}')
        return

    if poll.has_already_voted(msg.author):
        print('DUPE')
        return

    poll.add_vote(msg.author, choice)


@Command('listpolls', help='list all active polls', permission=LIST_POLLS_PERMISSION)
async def cmd_list_polls(msg: Message, *args):
    await msg.reply(' | '.join(f'{poll.id} -> "{poll.title}"' for poll in get_active_channel_polls(msg.channel_name)))


@Command('pollinfo', syntax='(POLL_ID)', help='views info about the poll using the passed poll id', permission=POLL_INFO_PERMISSION)
async def cmd_poll_info(msg: Message, *args):
    count = get_active_channel_poll_count(msg.channel_name)

    if not count:
        await msg.reply('there are not any polls active right now')
        return

    if count > 1 and not args:
        raise InvalidArgumentsError(
            reason=f'multiple polls are running, the poll id is required to be passed, example: {cfg.prefix}pollinfo <POLL_ID>',
            cmd=cmd_poll_info
        )

    if count == 1:
        poll = get_active_channel_polls(msg.channel_name)[0]
    else:
        poll_id = _cast_to_int_or_error(args[0], cmd_poll_info)
        poll = get_channel_poll_by_id(msg.channel_name, poll_id)

        if poll is None:
            raise InvalidArgumentsError(reason=f'could not find any poll by ID {poll_id}', cmd=cmd_poll_info)

    await msg.reply(f'POLL INFO #{poll.id} - title: "{poll.title}" - choices: {poll.format_choices()} - seconds left: {poll.seconds_left}')


def _cast_to_int_or_error(value: str, src_cmd) -> int:
    if not value.isdigit():
        raise InvalidArgumentsError(reason=f'{value} is not a valid number', cmd=src_cmd)
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
