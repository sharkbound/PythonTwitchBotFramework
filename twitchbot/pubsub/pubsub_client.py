import warnings
import json
import websockets

from typing import Optional
from asyncio import sleep

__all__ = [
    'PubSubClient',
    'PubSubKeys'
]


class PubSubKeys:
    nonce = 'nonce'
    listen = 'listen'
    error = 'error'
    type = 'type'


class PubSubClient:
    TASK_NAME = 'pubsub_client_processor'
    PUBSUB_WEBSOCKET_URL = 'wss://pubsub-edge.twitch.tv'
    NONCE_REQUEST_VALUE = 'NONCE'
    LISTEN_REQUEST_KEY = 'LISTEN'

    def __init__(self):
        self.socket: Optional[websockets.client.WebSocketClientProtocol] = None
        self.listen_count = 0

    @classmethod
    async def _create_channel_points_topic(cls, channel_name: str) -> Optional[str]:
        from ..util import get_user_id

        user_id = await get_user_id(channel_name)
        if user_id == -1:
            warnings.warn(f'[PUBSUB-CLIENT] unable to get user id in pubsub client for channel "{channel_name}"')
            return None

        return f'channel-subscribe-events-v1.{user_id}'

    @classmethod
    async def _create_channel_chat_topic(cls, channel_name: str) -> Optional[str]:
        from ..util import get_user_id

        user_id = await get_user_id(channel_name)
        if user_id == -1:
            warnings.warn(f'[PUBSUB-CLIENT] unable to get user id in pubsub client for channel "{channel_name}"')
            return None

        return f'chat_moderator_actions.{user_id}'

    @property
    def connected(self):
        return self.socket and self.socket.open

    def create_listen_request_data(self, nonce: str = None, topics=(), access_token: str = '') -> str:
        """
        returns the json data (as a string) for listening to topic(s) on twitch's PUBSUB
        :param nonce: optional identifier for the request
        :param topics: topics to listen to on PUBSUB
        :param access_token: access token used to LISTEN to a channel's PUBSUB
        """
        from twitchbot import get_oauth

        data = {
            'type': self.LISTEN_REQUEST_KEY,
            'data': {
                'topics': topics,
                'auth_token': access_token or get_oauth(remove_prefix=True),
            },
        }

        if nonce:
            data[self.NONCE_REQUEST_VALUE] = nonce

        return json.dumps(data)

    async def listen_to_channel(self, channel_name: str, points: bool = True, chat: bool = True, access_token: str = '', nonce=None):
        if not self.socket or not self.socket.open:
            await self._connect()
            await sleep(.5)

        await sleep(.5)  # small thing to rate limit to a degree

        topics = []

        if points:
            topics.append(await self._create_channel_points_topic(channel_name))

        if chat:
            topics.append(await self._create_channel_chat_topic(channel_name))

        if not topics:
            return

        await self.socket.send(
            self.create_listen_request_data(topics=topics, access_token=access_token, nonce=nonce or channel_name)
        )

    async def read(self) -> Optional[str]:
        data = await self.socket.recv()
        if isinstance(data, bytes):
            return data.decode('utf-8')
        return data

    async def _connect(self) -> 'PubSubClient':
        self.socket = await websockets.connect(self.PUBSUB_WEBSOCKET_URL)
        return self

    def start_loop(self):
        from ..util import add_task, task_exist
        if not task_exist(self.TASK_NAME):
            add_task(self.TASK_NAME, self._processor_loop())

    async def _processor_loop(self):
        while True:
            if self.socket is not None:
                try:
                    data = json.loads(await self.read())
                except (json.JSONDecodeError, TypeError):
                    continue

                await self._trigger_events(data)
            else:
                await sleep(2)

    async def _trigger_events(self, data):
        from ..event_util import forward_event, Event
        forward_event(Event.on_pubsub_received, data)
