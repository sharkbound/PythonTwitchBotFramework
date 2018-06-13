from asyncio import get_event_loop

from twitchbot import (
    Command,
    cfg,
    Message,
    InvalidArgumentsException,
    SongRequestCommand,
    send_song_request_command,
    get_youtube_video_info,
    thread_pool,
    YoutubeVideo,
    has_song_request_clients
)


@Command('sr', syntax='<video_name | video_id | video_url>', help='enqueues a song to be played on song request')
async def cmd_sr(msg: Message, *args):
    if not args:
        raise InvalidArgumentsException()

    if not has_song_request_clients():
        await msg.reply(f'{msg.mention} there are not any clients connected to send song request to right now')
        return

    if msg.channel_name != cfg.owner:
        await msg.reply(f'{cmd_sr.fullname} can only be run from the owners channel')
        return

    query = ' '.join(args)
    video: YoutubeVideo = await get_event_loop().run_in_executor(thread_pool, get_youtube_video_info, query)

    if not video:
        await msg.reply(f'no video found for "{query}"')
        return

    await send_song_request_command(SongRequestCommand.PLAY, video.id)
    await msg.reply(
        f'{msg.mention} enqueued "{video.title}" uploaded by "{video.uploader}", video is {video.duration/60:.2f} minutes long')


@Command('skip', permission='skip', help='skips the current song playing on song request')
async def cmd_skip(msg: Message, *args):
    if not has_song_request_clients():
        await msg.reply(f'{msg.mention} there are no clients connected to send a skip request to')
        return

    await send_song_request_command(SongRequestCommand.SKIP)
    await msg.reply(f'{msg.mention} skipped the current song')
