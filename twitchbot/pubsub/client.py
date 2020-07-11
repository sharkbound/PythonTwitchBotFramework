from typing import Optional

from websockets import connect, WebSocketClientProtocol

__all__ = [
    'PubSubClient'
]

PUBSUB_URL = 'wss://pubsub-edge.twitch.tv'


class PubSubClient:
    def __init__(self):
        self.socket: Optional[WebSocketClientProtocol] = None
