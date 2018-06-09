from collections import deque
from concurrent.futures import ThreadPoolExecutor
from asyncio import get_event_loop
from youtube_dl import YoutubeDL
from subprocess import call
from . import FFMPEG_PATH
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
        # if not self.can_play:
        #     return

        song = self.songs.popleft()
        call(song.file_name, )
        # os.startfile(f'')
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
ytdl = YoutubeDL(YTDL_FORMAT)
song_player = SongPlayer()
