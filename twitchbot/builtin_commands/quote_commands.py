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
    InvalidArgumentsError
)

PREFIX = cfg.prefix


@Command('addquote', syntax='"<quote text>" user=(user) alias=(alias)', help='adds a quote to the database')
async def cmd_add_quote(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required arguments', cmd=cmd_add_quote)

    optionals = ' '.join(args[1:])

    user = alias = None
    if 'user=' in optionals:
        m = re.search(r'user=([\w\d]+)', msg.content)
        if not m:
            raise InvalidArgumentsError(
                reason='invalid user for user=, must be a combination of digits and letters, ex: john_doe17',
                cmd=cmd_add_quote)

        user = m.group(1)

    if 'alias=' in optionals:
        m = re.search(r'alias=([\d\w]+)', msg.content)
        if not m:
            raise InvalidArgumentsError(
                reason='invalid alias for alias=, must be a combination of digits and letters, ex: my_quote1',
                cmd=cmd_add_quote)

        alias = m.group(1)
        if get_quote_by_alias(msg.channel_name, alias) is not None:
            raise InvalidArgumentsError(reason='there is already a quote with that alias', cmd=cmd_add_quote)

    quote = Quote.create(channel=msg.channel_name, value=args[0], user=user, alias=alias)
    if add_quote(quote):
        resp = f'successfully added quote #{quote.id}'
    else:
        resp = 'failed to add quote, already exist'

    await msg.reply(resp)


@Command('quote', syntax='<ID or ALIAS>', help='gets a quote by ID or ALIAS')
async def cmd_get_quote(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required argument', cmd=cmd_get_quote)

    quote = get_quote(msg.channel_name, args[0])
    if quote is None:
        raise InvalidArgumentsError(reason='no quote found', cmd=cmd_get_quote)

    await msg.reply(f'"{quote.value}" user: {quote.user} alias: {quote.alias}')


@Command('delquote', permission='delete_quote', syntax='<ID or ALIAS>', help='deletes the quote from the database')
async def cmd_del_quote(msg: Message, *args):
    if not args:
        raise InvalidArgumentsError(reason='missing required argument', cmd=cmd_del_quote)

    quote = get_quote(msg.channel_name, args[0])
    if quote is None:
        raise InvalidArgumentsError(reason='no quote found', cmd=cmd_del_quote)

    delete_quote_by_id(msg.channel_name, quote.id)
    await msg.reply(f'successfully deleted quote, id: {quote.id}, alias: {quote.alias}')
