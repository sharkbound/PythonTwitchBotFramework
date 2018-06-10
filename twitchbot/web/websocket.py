from asyncio import get_event_loop, sleep
from typing import List
from ..enums import SongRequestCommand
import websockets as ws
from websockets.server import WebSocketServerProtocol


async def handle_song_request_client(socket: WebSocketServerProtocol, ignored):
    song_request_clients.append(socket)

    while socket.open:
        await sleep(1)

    song_request_clients.remove(socket)


async def _socket_server_main():
    server = await ws.serve(handle_song_request_client, 'localhost', 9999, )
    await server.wait_closed()


def start_socket_server():
    get_event_loop().create_task(_socket_server_main())


song_request_clients: List[WebSocketServerProtocol] = []


async def send_song_request_command(command: SongRequestCommand, *args):
    for client in song_request_clients:
        await client.send(f'{command.value} {" ".join(args)}')
