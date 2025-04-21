import asyncio
from enum import Enum, auto
from typing import Optional

import websockets

EVENTSUB_WEBSOCKET_URL = 'wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=600'
WS_CONNECTING, WS_OPEN, WS_CLOSING, WS_CLOSED = range(4)

class EventSubConnectionState(Enum):
    UNINITIALIZED = auto()
    CONNECTED = auto()
    RECONNECT_REQUESTED = auto()
    DISCONNECTED = auto()


class EventSubClient:
    def __init__(self):
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.state: EventSubConnectionState = EventSubConnectionState.UNINITIALIZED
        self.session_id: Optional[str] = None

    async def connect(self):
        self.ws = await websockets.connect(EVENTSUB_WEBSOCKET_URL)

    async def _raw_read_next_str(self, timeout: float = 10) -> Optional[str]:
        if self.ws.state != WS_OPEN:
            return None

        try:
            return await asyncio.wait_for(self.ws.recv(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def listen(self, access_token: str, ):
        pass

    async def listen_loop(self):
        while True:
            try:
                event = await self.ws.recv()
            except:
                print('Lost connection to EventSub server.')
                return
            # Process the event here
            if event:
                print('\nreceived event:', event)
            else:
                print(end='.')
