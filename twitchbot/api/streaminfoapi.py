from datetime import datetime

from .baseapi import Api
from .. import util


class StreamInfoApi(Api):
    def __init__(self, client_id: str, user: str):
        super().__init__(client_id, user)

        self.viewer_count: int = 0
        self.title: str = ''
        self.game_id: int = 0
        self.community_ids: frozenset = frozenset()
        self.started_at: datetime = datetime.min
        self.user_id: int = 0
        self.tag_ids: frozenset = frozenset()

    async def update(self, log=False):
        """
        requests the updated stream info from twitch, called every X seconds (default 60)

        calls `self.on_successful_update` when it updates without errors

        calls `self.on_failed_update` when the update fails, (usually due to key errors)

        :param log: should errors be logged?
        """
        data = await util.get_stream_data(self.user, self.headers)
        try:
            self.viewer_count = data['viewer_count']
            self.title = data['title']
            self.game_id = data['game_id']
            self.community_ids = frozenset(data['community_ids'])
            #                                                      2018-05-17T16:47:46Z
            self.started_at = datetime.strptime(data['started_at'], '%Y-%m-%dT%H:%M:%SZ')
            self.user_id = data['user_id']
            self.tag_ids = frozenset(data['tag_ids'])

            await self.on_successful_update()
        except KeyError as e:
            if log:
                print(f'[STREAM INFO API] failed to update stream data for {self.user}')
                print(f'[STREAM INFO API] key error occurred while trying to access key: {e}')

            await self.on_failed_update()
