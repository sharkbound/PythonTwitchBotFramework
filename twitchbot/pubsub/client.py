import asyncio
import json
import time
import warnings
import websockets

from asyncio import sleep
from typing import Optional, Iterable

from ..enums import Event

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
    RECONNECT_PONG_TIMEOUT = 10

    def __init__(self):
        self.socket: Optional[websockets.client.WebSocketClientProtocol] = None
        self.listen_count = 0
        self._last_ping_sent_time = time.time()
        self._waiting_for_pong = False
        self._pong_received = False
        self._previously_sent_listen_data = set()

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

    def _mark_pong_received(self):
        self._pong_received = True
        self._waiting_for_pong = False

    def _mark_ping_sent(self):
        self._pong_received = False
        self._waiting_for_pong = True
        self._last_ping_sent_time = time.time()

    def _check_needs_reconnect(self):
        return not self.connected or (
                self._waiting_for_pong
                and not self._pong_received
                and self.last_ping_time_diff > self.RECONNECT_PONG_TIMEOUT
        )

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

        listen_data = self.create_listen_request_data(topics=topics, access_token=access_token, nonce=nonce or channel_name).strip()
        if listen_data not in self._previously_sent_listen_data:
            self._previously_sent_listen_data.add(listen_data)

        await self.socket.send(listen_data)
        return True

    @property
    def last_ping_time_diff(self):
        return abs(time.time() - self._last_ping_sent_time)

    @property
    def last_ping_time_diff_minutes(self):
        return abs(time.time() - self._last_ping_sent_time) / 60

    async def _send_ping(self):
        await self.socket.send(json.dumps({'type': 'PING'}))
        self._mark_ping_sent()

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

    async def _reconnect(self, listen_resend_interval=.7, reconnect_interval=5) -> bool:
        import socket

        for retry in range(10):
            try:
                warnings.warn(f'[PUBSUB_CLIENT] attempting reconnect #{retry}...')
                await self._connect()

                # make sure connection is actually open
                if not self.socket and not self.socket.open:
                    raise ValueError

                # resend pubsub listen request
                for listen_data in self._previously_sent_listen_data:
                    await self.socket.send(listen_data)
                    await asyncio.sleep(listen_resend_interval)

                # signal reconnect was successful
                return True
            except (ValueError, socket.gaierror):
                warnings.warn(f'[PUBSUB_CLIENT] reconnect #{retry} failed... trying again in {reconnect_interval} seconds...')
                await asyncio.sleep(reconnect_interval)

        # signal reconnect was unsuccessful
        return False

    async def _processor_loop(self):
        while True:
            if self.socket is not None:
                # keep reconnect logic behind the socket is not None check to be sure we had a previous connection
                if self._check_needs_reconnect():
                    await self._reconnect_loop()

                try:
                    await self._read_and_handle()
                except (json.JSONDecodeError, TypeError):
                    pass
                except websockets.exceptions.ConnectionClosedError:
                    # allow reconnect logic to try to re-establish a connection
                    continue

                await self._send_ping_if_needed()
                if self._check_needs_reconnect():
                    await self.socket.close()
            else:
                await sleep(2)

    async def _reconnect_loop(self):
        while True:
            if await self._reconnect():
                break

            warnings.warn('[PUBSUB_CLIENT] reconnect failed, retrying in 5 minutes')
            await asyncio.sleep(60 * 5)

    async def _read_and_handle(self):
        raw_resp = await self.read(timeout=10)
        data = PubSubData(json.loads(raw_resp))

        if data.is_pong:
            self._mark_pong_received()

        await self._trigger_events(data)

    async def _trigger_events(self, data: 'PubSubData'):
        from ..event_util import forward_event
        forward_event(Event.on_pubsub_received, data)

        # checks for and runs a matching pubsub event
        (
                self._check_for_channel_point_redemption(data)
                or self._check_for_bits(data)
                or self._check_for_moderation_action(data)
                or self._noop()
        )

    def _noop(self, *_):
        pass

    def _check_for_channel_point_redemption(self, data: 'PubSubData'):
        from ..event_util import forward_event
        from .point_redemption_model import PubSubPointRedemption

        if not data.is_channel_points_redeemed:
            return False

        forward_event(Event.on_pubsub_custom_channel_point_reward, data, PubSubPointRedemption(data))
        return True

    def _check_for_bits(self, data: 'PubSubData'):
        from ..event_util import forward_event
        from .bits_model import PubSubBits

        if not data.is_bits:
            return False

        forward_event(Event.on_pubsub_bits, data, PubSubBits(data))
        return True

    def _check_for_moderation_action(self, data: 'PubSubData'):
        from ..event_util import forward_event
        from .pubsub_moderation_action import PubSubModerationAction

        if not data.is_moderation_action:
            return False

        forward_event(Event.on_pubsub_moderation_action, data, PubSubModerationAction(data))
        return True

    async def _send_ping_if_needed(self):
        if self.last_ping_time_diff >= self.PING_SEND_INTERVAL:
            await self._send_ping()
