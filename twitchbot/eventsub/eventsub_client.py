import asyncio
import time
import warnings
from enum import Enum, auto
from typing import Optional, Iterable

import websockets
import aiohttp

from .eventsub_message_parsers import parse_eventsub_json
from .eventsub_topics import EventSubTopics
from ..util import get_user_id
from ..config import get_client_id

from .eventsub_message_types import EventSubMessage, EventSubMessageType

EVENTSUB_WEBSOCKET_URL = "wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=300"
WS_CONNECTING, WS_OPEN, WS_CLOSING, WS_CLOSED = range(4)


class EventSubConnectionState(Enum):
    UNINITIALIZED = auto()
    RECONNECT_REQUESTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    CLOSED = auto()


class EventSubClient:
    def __init__(self):
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.session_id: Optional[str] = None
        self.keepalive_seconds_interval: int = 600
        self.last_keepalive_timestamp: float = time.time()
        self._client_connection_state: EventSubConnectionState = EventSubConnectionState.UNINITIALIZED
        self.reconnect_url: Optional[str] = EVENTSUB_WEBSOCKET_URL

    def seconds_since_last_keepalive(self) -> int:
        return int(time.time() - self.last_keepalive_timestamp)

    def _update_connection_state_from_websocket_state(self):
        # if a reconnect is requested, the websocket needs to be closed, then reconnected, so do nothing.
        if self._client_connection_state is EventSubConnectionState.RECONNECT_REQUESTED:
            return

        elif self.ws is None:
            self._client_connection_state = EventSubConnectionState.UNINITIALIZED

        elif self.ws.state == WS_CONNECTING:
            self._client_connection_state = EventSubConnectionState.CONNECTING

        elif self.ws.state == WS_CLOSED or self.ws.state == WS_CLOSING:
            self._client_connection_state = EventSubConnectionState.CLOSED

        else:
            self._client_connection_state = EventSubConnectionState.CONNECTED

    @property
    def is_connected(self) -> bool:
        return self.ws is not None and self.ws.open

    async def disconnect(self):
        if self.ws is None:
            return

        if self.is_connected:
            await self.ws.close()
            self.ws = None
            self._client_connection_state = EventSubConnectionState.UNINITIALIZED

    async def connect(self) -> bool:
        """
        Connects to EventSub via WebSocket and verifies that it receives a welcome message.
        If a welcome message is not received, the connection is considered unsuccessful.
        Also updates the internal connection state accordingly.
        Returns True if connection is successful, False otherwise.
        """
        if self.is_connected:
            return True

        self.ws = await websockets.connect(EVENTSUB_WEBSOCKET_URL)
        resp = (await self.read_next())
        if resp is None:
            warnings.warn(
                "[EventSubClient.connect] Did not receive a welcome message. Without it, session_id is not known, so EventSubClient cannot function.")
            await self.disconnect()
            return False

        self._client_connection_state = EventSubConnectionState.CONNECTED
        return True

    async def _raw_read_next_str(self, timeout: float = 10) -> Optional[str]:
        if not self.is_connected:
            return None

        try:
            return await asyncio.wait_for(self.ws.recv(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def read_next(self) -> Optional['EventSubMessage']:
        val = await self._raw_read_next_str()
        message = parse_eventsub_json(val)
        await self._process_message(message)
        return message

    async def _process_message(self, message: Optional['EventSubMessage']):
        if message is None:
            return

        # debug
        print(f'[EventSubClient] Received message ({message.message_type}): {message.as_generic().pretty_printed_str()}')

        if message.message_type is EventSubMessageType.SESSION_WELCOME:
            message = message.as_welcome_message()
            self.session_id = message.session_id
            self.keepalive_seconds_interval = message.keepalive_timeout_seconds
            print(f'[EventSubClient] Now connected to Twitch EventSub Websocket server. Keepalive interval: {self.keepalive_seconds_interval}.')
        elif message.message_type is EventSubMessageType.SESSION_KEEPALIVE:
            self.last_keepalive_timestamp = time.time()
        elif message.message_type is EventSubMessageType.REVOCATION:
            # todo: Trigger events for revocation
            pass
        elif message.message_type is EventSubMessageType.NOTIFICATION:
            # todo: Trigger events for notifications
            pass
        elif message.message_type is EventSubMessageType.SESSION_RECONNECT:
            self.reconnect_url = message.as_reconnect_message().reconnect_url
            self._client_connection_state = EventSubConnectionState.RECONNECT_REQUESTED

    async def subscribe(self, access_token: str, channel_name: str, topics: Iterable[EventSubTopics]) -> bool:
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
            connection_successful = await self.connect()
            if not connection_successful:
                return False

        async with aiohttp.ClientSession() as session:
            for topic in topics:
                print(f'Subscribing to {topic.name}')  # debug
                headers = {
                    'Client-Id': get_client_id(),
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                data = {
                    'type': topic.value,
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
                        error_message = f"Failed to subscribe to {topic.name}: {resp.status} - {resp_json.get('message', 'Unknown error')}"
                        print(f"[EventSubClient] {error_message}")
                        # await self.on_failed_subscription(topic, resp.status, resp_json)
                        return False
                    else:
                        return True
                except Exception as e:
                    error_message = f"Exception while subscribing to {topic.name}: {str(e)}"
                    warnings.warn(f"[EventSubClient] {error_message}", stacklevel=2)
                    return False
                    # await self.on_failed_subscription(topic, None, {"error": str(e)})
        return False
