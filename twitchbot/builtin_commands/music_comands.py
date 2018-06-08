from twitchbot import (
    Message,
    Command,
)

from collections import deque
from concurrent.futures import ThreadPoolExecutor
from asyncio import get_event_loop
import youtube_dl as yt
import typing
import os


class SongPlayer:
    def __init__(self, *songs):
        self.songs: typing.Deque[Song] = deque(songs)
        self.current_song: Song = None

    @property
    def can_play(self):
        return self.songs and not self.current_song

    def queue(self, song: 'Song'):
        if not song or song in self.songs:
            return

        self.songs.append(song)

    def play(self):
        if not self.can_play:
            return

        song = self.songs.popleft()
        os.startfile(song.file_name)
        self.current_song = song


class Song:
    def __init__(self, id: str, title: str, ext: str):
        self.title: str = title
        self.ext: str = ext
        self.id: str = id
        self.file_name: str = f'{self.id}.{self.ext}'

    def __str__(self):
        return f'<Song id={self.id} file_name={self.file_name} ext={self.ext}>'


YTDL_FORMAT = {
    'format': 'bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s'
}

loop = get_event_loop()
pool = ThreadPoolExecutor(2)
ytdl = yt.YoutubeDL(YTDL_FORMAT)
song_player = SongPlayer()


def _download(url: str):
    print('starting song download:', url)
    info = ytdl.extract_info(url)
    song = Song(info['id'], info['title'], info['ext'])
    song_player.queue(song)
    print('done downloading:', song)
    song_player.play()


@Command('sr')
async def cmd_sr(msg: Message, *args):
    loop.run_in_executor(pool, _download, 'https://www.youtube.com/watch?v=8dZDdW7v4Q8')
