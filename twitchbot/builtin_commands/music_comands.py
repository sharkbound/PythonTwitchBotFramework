from twitchbot import (
    Command,
    cfg,
    Message,
    InvalidArgumentsException
)


@Command('sr')
async def cmd_sr(msg: Message, *args):
    if not args:
        raise InvalidArgumentsException()

    if msg.channel_name != cfg.owner:
        await msg.reply(f'{cmd_sr.fullname} can only be run from the owners channel')
        return
