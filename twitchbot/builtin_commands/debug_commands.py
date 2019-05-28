from twitchbot import Message, Command, get_user_info


@Command('ping', permission='ping')
async def cmd_debug(msg: Message, *args):
    await msg.reply('Pong!')


# @Command('info', permission='info')
async def cmd_info(msg: Message, *args):
    info = await get_user_info(args[0])
    await msg.reply(
        ' | '.join(map(str, (
            info.type,
            info.id,
            info.broadcaster_type,
            info.description,
            info.display_name,
            info.login,
            info.offline_image_url,
            info.profile_image_url,
            info.view_count
        )))
    )
