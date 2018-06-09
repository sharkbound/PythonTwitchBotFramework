from twitchbot import (
    Command,
    ytdl,
    song_player,
    Message,
    Song,
    loop,
    pool,
    cfg,
    InvalidArgumentsException
)


def _download(url: str):
    print('starting song download:', url)
    info = ytdl.extract_info(url)
    song = Song(info['id'], info['title'], info['ext'])
    song_player.queue(song)
    print('done downloading:', song)
    song_player.play()


@Command('sr')
async def cmd_sr(msg: Message, *args):
    if not args:
        raise InvalidArgumentsException()

    if msg.channel_name != cfg.owner:
        await msg.reply(f'{cmd_sr.fullname} can only be run from the owners channel')
        return

    loop.run_in_executor(pool, _download, args[0])
