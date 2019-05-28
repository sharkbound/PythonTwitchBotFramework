from twitchbot import Message, Command, get_user_info, format_datetime, get_user_creation_date, get_user_followers

#
# @Command('ping', permission='ping')
# async def cmd_debug(msg: Message, *args):
#     await msg.reply('Pong!')


# @Command('shoutout', permission='shoutout')
# async def cmd_shoutout(msg: Message, *args):
#     info = await get_user_info(args[0])
#     date = format_datetime(await get_user_creation_date(args[0]))
#     followers = await get_user_followers(args[0])
#
#     await msg.reply(f'go give {args[0]} a follow at {f"https://twitch.tv/{args[0]}"}')
#     await msg.reply(
#         f'{args[0]} with {followers.follower_count} followers and {info.view_count} views * created at {date}')
