import asyncio
import json
import getpass
from typing import Optional, List

import websockets
from socket import socket


class Connection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None

    async def connect(self):
        self.websocket = await websockets.connect(f'ws://{self.host}:{self.port}')

    async def read(self) -> str:
        return (await self.websocket.recv()).strip()

    async def read_json(self) -> dict:
        try:
            return json.loads(await self.read())
        except (json.JSONDecoder, TypeError):
            return {}

    async def send(self, text: str):
        await self.websocket.send(f'{text}')

    async def send_json(self, **kwargs):
        await self.send(json.dumps(kwargs))


class _RequestType:
    SEND_PASSWORD = 'send_password'
    BAD_PASSWORD = 'bad_password'
    DISCONNECTING = 'disconnecting'
    LIST_CHANNELS = 'list_channels'
    BAD_DATA = 'bad_data'
    AUTHENTICATION_SUCCESSFUL = 'authentication_successful'
    SEND_PRIVMSG = 'send_privmsg'
    CHANNEL_NOT_FOUND = 'channel_not_found'
    SUCCESS = 'success'


async def run():
    host = input('enter command server host (leave blank for "localhost"): ').strip() or 'localhost'
    port = int(input('enter command server port (leave blank for 1337): ').strip() or 1337)
    connection = Connection(host, port)
    channels: List[str] = []
    await connection.connect()

    while True:
        data = await connection.read_json()
        type = data['type']

        if type == _RequestType.SEND_PASSWORD:
            await connection.send(getpass.getpass('enter password for server >>> ').strip())
        elif type == _RequestType.DISCONNECTING:
            print('server terminated connection...')
            return
        elif type == _RequestType.BAD_PASSWORD:
            print('authentication failed... password did not match!')
            return
        elif type == _RequestType.LIST_CHANNELS:
            channels = data['data']['channels']
            print(f'bot is in these channels: {", ".join(channels)}')
        elif type == _RequestType.AUTHENTICATION_SUCCESSFUL:
            print('logged in to command server!')
            print('to select a channel to target, type /channel <channel>')


if __name__ == '__main__':
    asyncio.run(run())
