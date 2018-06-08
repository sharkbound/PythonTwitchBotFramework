from twitchbot import (
    Message,
    Command,
    SubCommand,
    DummyCommand
)

from collections import deque
from concurrent.futures import ThreadPoolExecutor
from asyncio import get_event_loop
import youtube_dl as yt

loop = get_event_loop()
pool = ThreadPoolExecutor(2)
ytdl = yt.YoutubeDL()
queue = deque()


def _download(url: str):
    print('starting song download:', url)
    ytdl.download([url])
    queue.append(url)
    print('done downloading:', url)
    print(queue)


@Command('sr')
async def cmd_sr(msg: Message, *args):
    loop.run_in_executor(pool, _download, 'https://www.youtube.com/watch?v=8dZDdW7v4Q8')
