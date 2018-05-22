import re

from command import Command
from message import Message
from database import (
    delete_quote_by_id,
    add_quote,
    get_quote_by_alias,
    get_quote,
)
from database.models import Quote
from config import cfg

PREFIX = cfg.prefix


@Command('addquote')
async def cmd_quote_add(msg: Message, *args):
    if not args:
        await msg.reply(f'invalid args: {PREFIX}addquote "<quote text>" user=(user) alias=(alias)')
        return

    optionals = ' '.join(args[1:])

    user = alias = None
    if 'user=' in optionals:
        m = re.search(r'user=(\w+)', msg.content)
        if not m:
            await msg.reply('invalid user')
            return

        user = m.group(1)

    if 'alias=' in optionals:
        m = re.search('alias=(\w+)', msg.content)
        if not m:
            await msg.reply('invalid alias')
            return

        alias = m.group(1)
        if get_quote_by_alias(msg.channel_name, alias) is not None:
            await msg.reply('there is already a quote with that alias')
            return

    if add_quote(Quote.create(channel=msg.channel_name, value=args[0], user=user, alias=alias)):
        resp = 'successfully added quote'
    else:
        resp = 'failed to add quote, already exist'

    await msg.reply(resp)


@Command('getquote')
async def cmd_get_quote(msg: Message, *args):
    if not args:
        await msg.reply(f'invalid args: {PREFIX}getquote <ID or ALIAS>')

    quote = get_quote(msg.channel_name, args[0])
    if quote is None:
        await msg.reply(f'no quote found')
        return

    await msg.reply(f'"{quote.value}" user: {quote.user} alias: {quote.alias}')


@Command('delquote', permission='delete_quote')
async def cmd_del_quote(msg: Message, *args):
    if not args:
        await msg.reply(f'invalid args: {PREFIX}delquote <ID or ALIAS>')

    quote = get_quote(msg.channel_name, args[0])
    if quote is None:
        await msg.reply(f'no quote found')
        return

    delete_quote_by_id(msg.channel_name, quote.id)

    await msg.reply(f'successfully deleted quote, id: {quote.id}, alias: {quote.alias}')
