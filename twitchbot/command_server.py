import json
from typing import Optional

import websockets
from asyncio import get_event_loop
from traceback import format_exc

from .channel import channels
from .config import cfg
from .util import add_task, task_running, stop_task

__all__ = [
    'start_command_server',
    'stop_command_server'
]

HOST = cfg.command_server_host
PORT = cfg.command_server_port
ENABLED = cfg.command_server_enabled
websocket_server: Optional[websockets.WebSocketServer] = None


# COMMAND_SERVER_TASK_ID = 'COMMAND_SERVER'


async def start_command_server():
    if not ENABLED:
        return

    stop_command_server()

    try:
        # noinspection PyTypeChecker
        global websocket_server
        websocket_server = await websockets.serve(handle_client, HOST, PORT)
        print(f'starting command server (view host / port in config file)')
    except Exception as e:
        print(f"\n------COMMAND SERVER------\nfailed to bind/create command server\n"
              f"this does not affect the bot, but it does mean that the command console will not work/be usable\n"
              f"if this error happens a lot, command server can be disabled in the config.json in the bot's configs folder\n"
              f'\nERROR INFO: {e}\n'
              f'EXTENDED INFO: \n{format_exc()}\n\n'
              f'------COMMAND SERVER------\n')


def stop_command_server():
    if websocket_server is not None and websocket_server.is_serving():
        websocket_server.close()


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
    RUN_COMMAND = 'run_command'


class ClientHandler:
    def __init__(self, websocket: websockets.WebSocketServerProtocol, path: str):
        self.path = path
        self.websocket = websocket
        self._running = True

    async def read(self):
        return (await self.websocket.recv()).strip()

    async def write_json(self, **data):
        await self.websocket.send(f'{json.dumps(data)}')

    async def handle_send_privmsg(self, data: dict):
        if 'channel' not in data:
            await self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'data for send_privmsg is missing `channel` key'})
            return

        if 'message' not in data:
            await self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'data for send_privmsg is missing `message` key'})
            return

        channel = data['channel'].lower().strip()
        if channel not in channels:
            await self.write_json(type=_RequestType.CHANNEL_NOT_FOUND, data={'reason': f'bot is not in requested channel `{channel}`'})
            return

        await channels[channel].send_message(data['message'])
        await self.write_json(type=_RequestType.SUCCESS, data={'type': _RequestType.SEND_PRIVMSG})

    async def _guard_run_cmd(self, data: dict):
        from .util import run_command
        from .irc import create_fake_privmsg

        try:
            await run_command(data['command'], create_fake_privmsg(data['channel'], ''), list(data['args']), blocking=True)
        except Exception as e:
            print(
                f'COMMAND SERVER [FAILED TO RUN COMMAND]: attempt to run command "{data["command"]}" with args {data["args"]} raised a error. details:\n\t'
                f'{e.__class__.__name__}: {e}')

    async def handle_run_command(self, data: dict):
        if 'channel' not in data:
            await self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'data for run_command is missing `channel` key'})
            return

        if 'command' not in data:
            await self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'data for run_command is missing `command` key'})
            return

        if 'args' not in data:
            await self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'data for run_command is missing `args` key'})
            return

        if not isinstance(data['args'], list):
            await self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'key `args` must be a list for `run_command`'})
            return

        get_event_loop().create_task(self._guard_run_cmd(data))
        await self.write_json(type=_RequestType.SUCCESS, data={'type': _RequestType.RUN_COMMAND})

    async def run(self):
        try:
            if cfg.command_server_password.strip():
                await self.write_json(type=_RequestType.SEND_PASSWORD, data={})
                password = await self.read()
                if password != cfg.command_server_password.strip():
                    await self.write_json(type=_RequestType.BAD_PASSWORD, data={})
                    await self.write_json(type=_RequestType.DISCONNECTING, data={})
                    return

            await self.write_json(type=_RequestType.AUTHENTICATION_SUCCESSFUL, data={})
            await self.write_json(type=_RequestType.LIST_CHANNELS, data={'channels': [channel.name for channel in channels.values()]})

            while self._running:
                try:
                    data = json.loads(await self.read())
                except (json.JSONDecodeError, TypeError):
                    await self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'response must be valid json'})
                    continue

                if not isinstance(data, dict):
                    await self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'data must be dictionary'})
                    continue

                if 'type' not in data:
                    await self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'data is must have the `type` key'})
                    continue

                msg_type = data['type']

                if msg_type == _RequestType.SEND_PRIVMSG:
                    await self.handle_send_privmsg(data)
                elif msg_type == _RequestType.RUN_COMMAND:
                    await self.handle_run_command(data)
        except ConnectionResetError:
            return


async def handle_client(websocket: websockets.WebSocketServerProtocol, path: str):
    await ClientHandler(websocket, path).run()
