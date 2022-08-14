import re

from twitchbot import (
    Command,
    Message,
    delete_quote_by_id,
    add_quote,
    get_quote_by_alias,
    get_quote,
    Quote,
    cfg,
    InvalidArgumentsError,
    translate,
    create_translate_callable,
)

PREFIX = cfg.prefix


@Command('addquote', permission='add_quote', syntax='"<quote text>" user=(user) alias=(alias)',
         help=create_translate_callable('builtin_command_help_message_addquote'))
async def cmd_add_quote(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_add_quote)

    optionals = ' '.join(args[1:])

    user = alias = None
    if 'user=' in optionals:
        m = re.search(r'user=([\w\d]+)', msg.content)
        if not m:
            raise InvalidArgumentsError(
                reason=translate('addquote_invalid_user'),
                cmd=cmd_add_quote)

        user = m.group(1)

    if 'alias=' in optionals:
        m = re.search(r'alias=([\d\w]+)', msg.content)
        if not m:
            raise InvalidArgumentsError(
                reason=translate('addquote_invalid_alias'),
                cmd=cmd_add_quote)

        alias = m.group(1)
        if get_quote_by_alias(msg.channel_name, alias) is not None:
            raise InvalidArgumentsError(reason=translate('addquote_duplicate_alias'), cmd=cmd_add_quote)

    quote = Quote.create(channel=msg.channel_name, value=args[0], user=user, alias=alias)
    if add_quote(quote):
        resp = translate('addquote_added', quote_id=quote.id)
    else:
        resp = translate('addquote_failed')

    await msg.reply(resp)


@Command('quote', syntax='<ID or ALIAS>', help=create_translate_callable('builtin_command_help_message_quote'))
async def cmd_get_quote(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_get_quote)

    quote = get_quote(msg.channel_name, args[0])
    if quote is None:
        raise InvalidArgumentsError(reason=translate('quote_not_found'), cmd=cmd_get_quote)

    await msg.reply(translate('quote_info', text=quote.value, user=quote.user, alias=quote.alias))


@Command('delquote', permission='delete_quote', syntax='<ID or ALIAS>', help=create_translate_callable('builtin_command_help_message_delquote'))
async def cmd_del_quote(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason=translate('missing_required_arguments'), cmd=cmd_del_quote)

    quote = get_quote(msg.channel_name, args[0])
    if quote is None:
        raise InvalidArgumentsError(reason=translate('quote_not_found'), cmd=cmd_del_quote)

    delete_quote_by_id(msg.channel_name, quote.id)
    await msg.reply(translate('delquote_deleted', quote_id=quote.id, alias=quote.alias))
