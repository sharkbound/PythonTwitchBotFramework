import youtube_dl as yt
from dataclasses import dataclass

ytdl = yt.YoutubeDL()


@dataclass
class YoutubeVideo:
    id: str
    title: str


async def get_yt_video_info(query: str):
    pass
