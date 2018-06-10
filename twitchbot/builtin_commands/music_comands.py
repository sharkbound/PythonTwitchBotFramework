from twitchbot import (
    Command,
    cfg,
    Message,
    InvalidArgumentsException,
    SongRequestCommand,
    send_song_request_command
)


@Command('sr')
async def cmd_sr(msg: Message, *args):
    if not args:
        raise InvalidArgumentsException()

    if msg.channel_name != cfg.owner:
        await msg.reply(f'{cmd_sr.fullname} can only be run from the owners channel')
        return

    await send_song_request_command(SongRequestCommand.PLAY, args[0])
