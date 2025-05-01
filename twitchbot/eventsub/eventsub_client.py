import asyncio
import warnings
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING, Iterable

import websockets
import aiohttp

from .eventsub_message_parsers import parse_eventsub_json
from .eventsub_topics import EventSubTopics
from ..util import get_user_id
from ..config import get_client_id

if TYPE_CHECKING:
    from .eventsub_message_types import EventSubMessage, EventSubMessageType

EVENTSUB_WEBSOCKET_URL = 'wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=600'
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

    @property
    def websocket_connection_state(self) -> EventSubConnectionState:
        if self.ws is None:
            return EventSubConnectionState.UNINITIALIZED

        if self.ws.state == WS_CONNECTING:
            return EventSubConnectionState.CONNECTING

        if self.ws.state == WS_CLOSED or self.ws.state == WS_CLOSING:
            return EventSubConnectionState.CLOSED

        return EventSubConnectionState.CONNECTED

    @property
    def is_connected(self) -> bool:
        return self.websocket_connection_state is EventSubConnectionState.CONNECTED

    async def connect(self):
        if self.is_connected:
            return

        self.ws = await websockets.connect(EVENTSUB_WEBSOCKET_URL)
        resp = (await self.read_next()).as_welcome_message()
        if resp is None:
            warnings.warn(
                "[EventSubClient.connect] Did not receive welcome message. Without it, session_id is not known, so EventSubClient cannot function.")
            return
        self.session_id = resp.session_id

    async def _raw_read_next_str(self, timeout: float = 10) -> Optional[str]:
        if not self.is_connected:
            return None

        try:
            return await asyncio.wait_for(self.ws.recv(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def read_next(self) -> 'EventSubMessage':
        val = await self._raw_read_next_str()
        return parse_eventsub_json(val)

    async def listen(self, access_token: str, channel_name: str, topics: Iterable[EventSubTopics]):
        print('Getting broadcaster id for', channel_name, '...') # debug
        broadcaster_id = await get_user_id(channel_name)
        print('Broadcaster id:', broadcaster_id) # debug
        # Here for clarity. This id is the user who authorized the app to access the channel.
        # For our purposes, it is the same as the broadcaster_id.
        moderator_id = broadcaster_id

        if not self.is_connected:
            print('EventSubClient is not connected. Attempting to connect now...') # debug
            await self.connect()
            print('Connected successfully. Session ID:', self.session_id) # debug

        async with aiohttp.ClientSession() as session:
            for topic in topics:
                print(f'Subscribing to {topic.name}') # debug
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
                resp = await session.post('https://api.twitch.tv/helix/eventsub/subscriptions', headers=headers, json=data)
                print(await resp.json())


