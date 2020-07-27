import asyncio
import json
import time
import warnings
from asyncio import sleep
from typing import Optional, Tuple, Iterable

import websockets

__all__ = [
    'PubSubClient',
]

from .models import PubSubData


class PubSubClient:
    TASK_NAME = 'pubsub_client_processor'
    PUBSUB_WEBSOCKET_URL = 'wss://pubsub-edge.twitch.tv'
    NONCE_REQUEST_VALUE = 'NONCE'
    LISTEN_REQUEST_KEY = 'LISTEN'
    PING_SEND_INTERVAL = 60 * 4.6

    def __init__(self):
        self.socket: Optional[websockets.client.WebSocketClientProtocol] = None
        self.listen_count = 0
        self._last_ping_sent_time = time.time()
        self._pong_received = False

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

    async def listen_to_channel(self, channel_name: str, topics: Iterable[str], access_token: str = '', nonce=None) -> bool:
        if not self.connected:
            self.start_loop()
            await self._connect()

        from ..util import get_user_id

        if not self.socket or not self.socket.open:
            await self._connect()
            await sleep(.5)

        await sleep(.5)  # small thing to rate limit to a degree

        user_id = await get_user_id(channel_name)
        if user_id == -1:
            warnings.warn(f'[PUBSUB-CLIENT] unable to get user id in pubsub client for channel "{channel_name}"')
            return False

        topics = [f'{topic}{user_id}' for topic in topics]
        if not topics:
            return False

        await self.socket.send(
            self.create_listen_request_data(topics=topics, access_token=access_token, nonce=nonce or channel_name)
        )

        return True

    @property
    def last_ping_time_diff(self):
        return abs(time.time() - self._last_ping_sent_time)

    @property
    def last_ping_time_diff_minutes(self):
        return abs(time.time() - self._last_ping_sent_time) / 60

    async def _send_ping(self):
        await self.socket.send(json.dumps({'type': 'PING'}))
        self._last_ping_sent_time = time.time()

    async def read(self, timeout: float = 10) -> Optional[str]:
        try:
            data = await asyncio.wait_for(self.socket.recv(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

        if isinstance(data, bytes):
            return data.decode('utf-8')
        return data

    async def _connect(self) -> 'PubSubClient':
        self.socket = await websockets.connect(self.PUBSUB_WEBSOCKET_URL)
        self._last_ping_sent_time = time.time()
        return self

    def start_loop(self):
        from ..util import add_task, task_exist
        if not task_exist(self.TASK_NAME):
            add_task(self.TASK_NAME, self._processor_loop())

    async def _processor_loop(self):
        while True:
            if self.socket is not None:
                try:
                    await self._read_and_handle()
                except (json.JSONDecodeError, TypeError):
                    pass

                await self._send_ping_if_needed()
            else:
                await sleep(2)

    async def _read_and_handle(self):
        raw_resp = await self.read(timeout=10)
        data = PubSubData(json.loads(raw_resp))
        await self._trigger_events(data)

    async def _trigger_events(self, data: 'PubSubData'):
        from ..event_util import forward_event
        from ..enums import Event
        forward_event(Event.on_pubsub_received, data)

    async def _send_ping_if_needed(self):
        if self.last_ping_time_diff >= self.PING_SEND_INTERVAL:
            await self._send_ping()
