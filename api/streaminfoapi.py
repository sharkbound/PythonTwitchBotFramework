import asyncio
import util

from datetime import datetime
from .baseapi import Api


class StreamInfoApi(Api):
    def __init__(self, client_id: str, user: str):
        super().__init__(client_id, user)

        self.viewer_count = 0
        self.title = ''
        self.game_id = 0
        self.community_ids = []
        self.started_at = datetime.min
        self.user_id = 0

    async def update(self, log=False):
        data = await util.get_stream_data(self.user, self.headers)
        try:
            self.viewer_count = data['viewer_count']
            self.title = data['title']
            self.game_id = data['game_id']
            self.community_ids = data['community_ids']
            #                                                      2018-05-17T16:47:46Z
            self.started_at = datetime.strptime(data['started_at'], '%Y-%m-%dT%H:%M:%SZ')
            self.user_id = data['user_id']
        except KeyError as e:
            if log:
                print(f'[STREAM INFO API] failed to update stream data for {self.user}')
