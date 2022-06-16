import re
from sqlalchemy import Integer

from twitchbot import (
    Command,
    Message,
    cfg,
    InvalidArgumentsError,
    get_counter_by_alias,
    add_counter,
    DBCounter,
    get_counter,
    delete_counter_by_id,
    set_counter,
    get_all_counters
)

PREFIX = cfg.prefix

@Command('addcounter', permission='manage_counter', syntax='<ALIAS>', help='adds a counter to the database')
async def cmd_add_counter(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_add_counter)

    alias = args[0]

    m = re.search(r'([\d\w]+)', alias)
    if not m:
        raise InvalidArgumentsError(
            reason='invalid alias , must be a combination of digits and letters, ex: my_counter1',
            cmd=cmd_add_counter)

    alias = m.group(1)
    if get_counter_by_alias(msg.channel_name, alias) is not None:
        raise InvalidArgumentsError(reason='there is already a counter with that alias', cmd=cmd_add_counter)

    counter = DBCounter.create(channel=msg.channel_name, alias=alias)
    if add_counter(counter):
        resp = f'successfully added counter #{counter.id}'
    else:
        resp = 'failed to add counter, already exist'

    await msg.reply(resp)


@Command('delcounter', permission='manage_counter', syntax='<ID or ALIAS>', help='deletes the counter from the database')
async def cmd_del_counter(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required argument', cmd=cmd_del_counter)

    counter = get_counter(msg.channel_name, args[0])
    if counter is None:
        raise InvalidArgumentsError(reason='no counter found', cmd=cmd_del_counter)

    delete_counter_by_id(msg.channel_name, counter.id)
    await msg.reply(f'successfully deleted counter, id: {counter.id}, alias: {counter.alias}')


@Command('setcounter', permission='manage_counter', syntax='alias=(alias) value=(value)', help='adds a counter to the database')
async def cmd_set_counter(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_set_counter)

    optionals = ' '.join(args[0:])

    alias = None
    if 'alias=' in optionals:
        m = re.search(r'alias=([\d\w]+)', msg.content)
        if not m:
            raise InvalidArgumentsError(
                reason='invalid alias for alias=, must be a combination of digits and letters, ex: my_counter1',
                cmd=cmd_set_counter)

        alias = m.group(1)
        if get_counter_by_alias(msg.channel_name, alias) is None:
            raise InvalidArgumentsError(reason='there is no counter with das alias', cmd=cmd_set_counter)

    value = None
    if 'value=' in optionals:
        m = re.search(r'value=([\d]+)', msg.content)
        if not m:
            raise InvalidArgumentsError(
                reason='invalid value, only numbers are allowed',
                cmd=cmd_set_counter)

        value = m.group(1)

    new_val = set_counter(channel=msg.channel_name, id_or_alias=alias, new_value=value)

    await msg.reply(f'The counter {alias} has been updated to {new_val}')

@Command('listcounters', permission='manage_counter', help='list all counters of the channel')
async def cmd_set_counter(msg: Message, *args):
    clist = ', '.join(str(x) for x in get_all_counters(msg.channel_name))
    await msg.reply(f'The following counters are available: {clist}')
