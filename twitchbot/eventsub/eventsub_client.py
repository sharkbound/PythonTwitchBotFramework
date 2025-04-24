import asyncio
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

import websockets

from .eventsub_message_parsers import parse_eventsub_json

if TYPE_CHECKING:
    from .eventsub_message_types import EventSubMessage

EVENTSUB_WEBSOCKET_URL = 'wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=600'
WS_CONNECTING, WS_OPEN, WS_CLOSING, WS_CLOSED = range(4)


class EventSubConnectionState(Enum):
    UNINITIALIZED = auto()
    RECONNECT_REQUESTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    CLOSING = auto()
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

        if self.ws.state == WS_CLOSED:
            return EventSubConnectionState.CLOSED

        if self.ws.state == WS_CLOSING:
            return EventSubConnectionState.CLOSING

        return EventSubConnectionState.CONNECTED

    @property
    def is_connected(self) -> bool:
        return self.websocket_connection_state is EventSubConnectionState.CONNECTED

    async def connect(self):
        if self.is_connected:
            return

        self.ws = await websockets.connect(EVENTSUB_WEBSOCKET_URL)

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

    async def listen(self, access_token: str, channel: str, topic: str):
        pass
