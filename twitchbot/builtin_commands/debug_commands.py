from random import randint

from twitchbot import Message, Command, get_user_info, format_datetime, get_user_creation_date, get_user_followers, \
    get_channel_chatters, override_event, Event, Mod, run_command

pings = 0


@Command('ping', cooldown=0)
async def cmd_debug(msg: Message, *args):
    global pings
    pings += 1
    await msg.reply(f'Pong #{pings}')

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
