import asyncio
import logging
import time
import typing
import warnings
from enum import Enum, auto
from typing import Optional, List, Tuple, Union

import websockets
import aiohttp

from .eventsub_message_parsers import parse_eventsub_json
from .eventsub_topics import EventSubTopics
from ..util import get_user_id
from ..config import get_client_id
from ..enums import Event

from .eventsub_message_types import EventSubMessage, EventSubMessageType

if typing.TYPE_CHECKING:
    from websockets.asyncio.client import ClientConnection

__all__ = (
    'EventSubClient',
    'get_eventsub_client'
)

EVENTSUB_WEBSOCKET_URL = "wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=300"


class EventSubConnectionState(Enum):
    UNINITIALIZED = auto()
    RECONNECT_REQUESTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    CLOSED = auto()


class EventSubClient:
    def __init__(self):
        self.ws: Optional[ClientConnection] = None
        self.session_id: Optional[str] = None
        self.keepalive_seconds_interval: int = 300
        self.last_keepalive_timestamp: float = time.time()
        self._client_connection_state: EventSubConnectionState = EventSubConnectionState.UNINITIALIZED
        self._reconnect_url: Optional[str] = EVENTSUB_WEBSOCKET_URL
        #                               access_token, channel_name, topic_str_val
        self._sent_topic_subscriptions_cache: List[Tuple[str, str, str]] = []
        self._processing_loop_task: Optional[asyncio.Task] = None

    def seconds_since_last_keepalive(self) -> int:
        return int(time.time() - self.last_keepalive_timestamp)

    def _update_connection_state_from_websocket_state(self):
        # if a reconnect is requested, the websocket needs to be closed, then reconnected, so do nothing.
        if self._client_connection_state is EventSubConnectionState.RECONNECT_REQUESTED:
            return

        elif self.ws is None:
            self._client_connection_state = EventSubConnectionState.UNINITIALIZED

        elif self.ws.state == websockets.State.CONNECTING:
            self._client_connection_state = EventSubConnectionState.CONNECTING

        elif self.ws.state == websockets.State.CLOSED or self.ws.state == websockets.State.CLOSING:
            self._client_connection_state = EventSubConnectionState.CLOSED

        else:
            self._client_connection_state = EventSubConnectionState.CONNECTED

    @property
    def is_connected(self) -> bool:
        return self.ws is not None and self.ws.state == websockets.State.OPEN

    async def disconnect(self):
        if self.ws is None:
            return

        if self.is_connected:
            await self.ws.close()
            self.ws = None
            self._client_connection_state = EventSubConnectionState.UNINITIALIZED
            if self._processing_loop_task is not None:
                self._processing_loop_task.cancel()
                self._processing_loop_task = None

    async def connect(self) -> bool:
        """
        Connects to EventSub via WebSocket and verifies that it receives a welcome message.
        If a welcome message is not received, the connection is considered unsuccessful.
        Also updates the internal connection state accordingly.
        Returns True if connection is successful, False otherwise.
        """
        if self.is_connected:
            return True

        self.ws = await websockets.connect(self._reconnect_url)
        resp = (await self.read_next()).as_welcome_message()
        if resp is None:
            warnings.warn(
                "[EventSubClient.connect] Did not receive a welcome message. Without it, session_id is not known, so EventSubClient cannot function.")
            await self.disconnect()
            return False

        self.keepalive_seconds_interval = resp.keepalive_timeout_seconds
        self.session_id = resp.session_id
        self._client_connection_state = EventSubConnectionState.CONNECTED

        print(
            f'[EventSubClient] Now connected to Twitch EventSub Websocket server. Keepalive interval: {self.keepalive_seconds_interval}s.')

        subs_to_remove = []
        if self._reconnect_url == EVENTSUB_WEBSOCKET_URL:  # reconnect url was from the original websocket url; we need to resend subscriptions.
            for i, (token, channel, topic) in enumerate(self._sent_topic_subscriptions_cache):
                if not await self.subscribe(token, channel, [topic]):
                    subs_to_remove.append(i)
                await asyncio.sleep(.2)
        else:  # reconnect url was from a reconnect request; we don't need to resend subscriptions.
            self._reconnect_url = EVENTSUB_WEBSOCKET_URL

        if self._processing_loop_task is not None and (self._processing_loop_task.done() or self._processing_loop_task.cancelled()):
            self._processing_loop_task = None

        if self._processing_loop_task is None:
            self._processing_loop_task = asyncio.ensure_future(self._processing_loop())

        # remove subscriptions that failed to subscribe
        for sub_i in reversed(subs_to_remove):
            del self._sent_topic_subscriptions_cache[sub_i]

        return True

    async def _raw_read_next_str(self, timeout: float = 10) -> Optional[str]:
        if not self.is_connected:
            return None

        try:
            return await asyncio.wait_for(self.ws.recv(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def _add_subscribe_to_cache(self, token: str, channel: str, topic: str):
        t = (token, channel, topic)
        if t not in self._sent_topic_subscriptions_cache:
            self._sent_topic_subscriptions_cache.append(t)

    def _remove_subscribe_from_cache(self, token: str, channel: str, topic: str):
        t = (token, channel, topic)
        if t in self._sent_topic_subscriptions_cache:
            self._sent_topic_subscriptions_cache.remove(t)

    async def read_next(self, timeout: float = 10) -> Optional['EventSubMessage']:
        val = await self._raw_read_next_str(timeout=timeout)
        if val is None:
            return None

        message = parse_eventsub_json(val)
        return message

    async def subscribe(self, access_token: str, channel_name: str, topics: List[Union[EventSubTopics, str]], _cache=True) -> bool:
        """
        Subscribes to the specified EventSub topics.
        If the EventSub client is not connected, it will attempt to connect to EventSub via WebSocket, then try to subscribe to the EventSub topics.
        Returns True if subscription is successful, False otherwise.
        """
        broadcaster_id = await get_user_id(channel_name)
        # Here for clarity. This id is the user who authorized the app to access the channel.
        # For our purposes, it is the same as the broadcaster_id.
        moderator_id = broadcaster_id

        if not self.is_connected:
            connection_successful = await self._connect_with_backoff(4)
            if not connection_successful:
                return False

        async with aiohttp.ClientSession() as session:
            for topic in topics:
                topic_str_val = topic.value if isinstance(topic, EventSubTopics) else topic
                headers = {
                    'Client-Id': get_client_id(),
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                data = {
                    'type': topic_str_val,
                    'version': '2',
                    'condition': {
                        'broadcaster_user_id': broadcaster_id,
                        'moderator_user_id': moderator_id,
                    },
                    'transport': {
                        'method': 'websocket',
                        'session_id': self.session_id
                    }
                }
                try:
                    resp = await session.post('https://api.twitch.tv/helix/eventsub/subscriptions', headers=headers, json=data)
                    resp_json = await resp.json()

                    if resp.status != 202:  # Twitch returns 202 Accepted for successful subscriptions
                        error_message = f"Failed to subscribe to {topic_str_val}: {resp.status} - {resp_json.get('message', 'Unknown error')}"
                        warnings.warn(f"[EventSubClient] {error_message}", stacklevel=2)
                        return False

                    if _cache:
                        self._add_subscribe_to_cache(access_token, channel_name, topic_str_val)

                    return True

                except Exception as e:
                    if _cache:
                        self._remove_subscribe_from_cache(access_token, channel_name, topic_str_val)
                    error_message = f"Exception while subscribing to {topic_str_val}: {str(e)}"
                    logging.warning(f"[EventSubClient] {error_message}", stacklevel=2)
                    return False

        return False

    async def _connect_with_backoff(self, max_tries: int = 10) -> bool:
        backoff_time = 1
        while True:
            if max_tries <= 0:
                return False
            try:
                if await self.connect():
                    break
            except Exception as e:
                logging.warning(f'[EventSubClient] Failed to connect to EventSub. Retrying in {backoff_time}s. Error: {str(e)}')
            else:  # No error
                logging.warning(f'[EventSubClient] Failed to connect to EventSub. Retrying in {backoff_time}s.')

            await asyncio.sleep(backoff_time)
            max_tries -= 1
            backoff_time <<= 2
        return True

    async def _processing_loop(self):
        TIMEOUT_SECONDS = 10
        while True:
            # initial check for if we are currently connected
            if not self.is_connected:
                await self._connect_with_backoff()

            # check if the last keepalive message has not been received in the specified keepalive interval
            if self.seconds_since_last_keepalive() > self.keepalive_seconds_interval:
                logging.warning(
                    f'[EventSubClient] No keepalive message received within {self.keepalive_seconds_interval} seconds. Attempting to reconnect.')
                await self.disconnect()
                if not await self._connect_with_backoff():
                    logging.error('[EventSubClient] Failed to reconnect to EventSub after disconnect.')
                    break
                continue

            message = await self.read_next(timeout=TIMEOUT_SECONDS)

            if message is None:
                continue

            from .. import forward_event
            forward_event(Event.on_raw_eventsub_received, message, message.channel_name())

            if message.message_type is EventSubMessageType.SESSION_WELCOME:
                message = message.as_welcome_message()
                self.session_id = message.session_id
                self.keepalive_seconds_interval = message.keepalive_timeout_seconds
                logging.info(
                    f'[EventSubClient] Now connected to Twitch EventSub Websocket server. Keepalive interval: {self.keepalive_seconds_interval}s.')

            elif message.message_type is EventSubMessageType.SESSION_KEEPALIVE:
                self.last_keepalive_timestamp = time.time()

            elif message.message_type is EventSubMessageType.REVOCATION:
                # todo: Trigger events for revocation
                pass

            elif message.message_type is EventSubMessageType.NOTIFICATION:
                # todo: Trigger events for notifications
                pass

            elif message.message_type is EventSubMessageType.SESSION_RECONNECT:
                self._reconnect_url = message.as_reconnect_message().reconnect_url
                self._client_connection_state = EventSubConnectionState.RECONNECT_REQUESTED


def get_eventsub_client() -> EventSubClient:
    return _eventsub_client


_eventsub_client = EventSubClient()
