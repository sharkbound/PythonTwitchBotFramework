import re

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
    get_all_counters,
    translate,
    counter_exist,
    create_translate_callable,
)

PREFIX = cfg.prefix


@Command('addcounter', permission='manage_counter', help=create_translate_callable('builtin_command_help_message_addcounter'))
async def cmd_add_counter(msg: Message, alias: str):
    m = re.search(r'([\d\w_]+)', alias)
    if not m or len(m.group(1)) != len(alias):
        raise InvalidArgumentsError(
            reason=translate('addcounter_invalid_alias'),
            cmd=cmd_add_counter
        )

    if get_counter_by_alias(msg.channel_name, alias) is not None:
        raise InvalidArgumentsError(reason=translate('addcounter_duplicate_alias'), cmd=cmd_add_counter)

    counter = DBCounter.create(channel=msg.channel_name, alias=alias)
    if add_counter(counter):
        resp = translate('addcounter_success', counter_id=counter.id)
    else:
        resp = translate('addcounter_already_exists')

    await msg.reply(resp)


@Command('delcounter', permission='manage_counter', syntax='<ID or ALIAS>', help=create_translate_callable('builtin_command_help_message_delcounter'))
async def cmd_del_counter(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_del_counter)

    counter = get_counter(msg.channel_name, args[0])
    if counter is None:
        raise InvalidArgumentsError(reason=translate('delcounter_not_found', query=args[0]), cmd=cmd_del_counter)

    delete_counter_by_id(msg.channel_name, counter.id)
    await msg.reply(translate('delcounter_deleted', counter_id=counter.id, counter_alias=counter.alias))


@Command('setcounter', permission='manage_counter', syntax='<alias_or_id> <new_value>',
         help=create_translate_callable('builtin_command_help_message_setcounter'))
async def cmd_set_counter(msg: Message, *args):
    if len(args) != 2:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_set_counter)

    alias_or_id, new_value = args
    counter = get_counter(msg.channel_name, alias_or_id)

    try:
        new_value = int(new_value)
    except ValueError:
        raise InvalidArgumentsError(reason=translate('setcounter_invalid_value'), cmd=cmd_set_counter)

    if counter is None:
        raise InvalidArgumentsError(reason=translate('delcounter_not_found', query=alias_or_id), cmd=cmd_set_counter)

    set_counter(msg.channel_name, alias_or_id, new_value)
    await msg.reply(translate('setcounter_success', counter=alias_or_id, new_val=new_value))


@Command('listcounters', permission='manage_counter', help=create_translate_callable('builtin_command_help_message_listcounters'))
async def cmd_list_counters(msg: Message, *args):
    clist = ', '.join(translate('listcounters_format', id=x.id, alias=x.alias, value=x.value) for x in get_all_counters(msg.channel_name))
    await msg.reply(translate('listcounters_list', clist=clist))
