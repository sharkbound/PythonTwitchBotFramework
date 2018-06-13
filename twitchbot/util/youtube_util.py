from concurrent.futures import ThreadPoolExecutor

import youtube_dl as yt
from typing import NamedTuple, Optional, Tuple

ytdl = yt.YoutubeDL(
    {'quiet': True, 'logtostderr': False, 'noplaylist': True, 'no_warnings': True, 'ignoreerrors': True})

thread_pool = ThreadPoolExecutor(2)


class YoutubeVideo(NamedTuple):
    id: str
    title: str
    uploader: str
    duration: int


def get_youtube_video_info(query: str) -> Optional[YoutubeVideo]:
    try:
        video = ytdl.extract_info(f'ytsearch:{query}', download=False)['entries'][0]
        return YoutubeVideo(video['id'], video['title'], video['uploader'], video['duration'])
    except (yt.DownloadError, TypeError, IndexError, KeyError):
        return None
