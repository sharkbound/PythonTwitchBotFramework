from twitchbot import Message, Command, CommandContext, translate

pings = -1


@Command('ping', cooldown=3)
async def cmd_ping(msg: Message, *args):
    global pings
    pings += 1
    await msg.reply(translate('ping_response', pings=pings))

# @Command('whisper', context=CommandContext.WHISPER)
# async def cmd_whisper(msg: Message, *args):
#     await msg.reply('got it!')

# @Command('shoutout', permission='shoutout')
# async def cmd_shoutout(msg: Message, *args):
#     info = await get_user_info(args[0])
#     date = format_datetime(await get_user_creation_date(args[0]))
#     followers = await get_user_followers(args[0])
#
#     await msg.reply(f'go give {args[0]} a follow at {f"https://twitch.tv/{args[0]}"}')
#     await msg.reply(
#         f'{args[0]} with {followers.follower_count} followers and {info.view_count} views * created at {date}')

# @Command('test')
# async def cmd_test(msg: Message, *args):
#     await msg.reply(f'{format_datetime(await get_user_creation_date(msg.author))}')
