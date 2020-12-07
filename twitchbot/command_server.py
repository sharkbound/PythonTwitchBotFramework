import json
from asyncio import start_server, StreamReader, StreamWriter
from traceback import format_exc

from .channel import channels, Channel
from .config import cfg
from .util import add_task, task_running, stop_task

__all__ = [
    'start_command_server',
    'stop_command_server'
]

HOST = cfg.command_server_host
PORT = cfg.command_server_port
ENABLED = cfg.command_server_enabled
COMMAND_SERVER_TASK_ID = 'COMMAND_SERVER'


def start_command_server():
    if not ENABLED:
        return

    stop_command_server()

    print(f'starting command server (view host / port in config file)')
    try:
        # noinspection PyTypeChecker
        add_task(COMMAND_SERVER_TASK_ID, start_server(handle_client, HOST, PORT))
    except Exception as e:
        print(f"\n------COMMAND SERVER------\nfailed to bind/create command server\n"
              f"this does not affect the bot, but it does mean that the command console will not work/be usable\n"
              f"if this error happens a lot, command server can be disabled in the config.json in the bot's configs folder\n"
              f'\nERROR INFO: {e}\n'
              f'EXTENDED INFO: \n{format_exc()}\n\n'
              f'------COMMAND SERVER------\n')


def stop_command_server():
    if task_running(COMMAND_SERVER_TASK_ID):
        stop_task(COMMAND_SERVER_TASK_ID)


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


class ClientHandler:
    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self.reader = reader
        self.writer = writer
        self._running = True

    async def read(self):
        return (await self.reader.readline()).decode('utf8').strip()

    def write_json(self, **data):
        self.writer.write(json.dumps(data).encode())

    async def handle_send_privmsg(self, data: dict):
        if 'channel' not in data:
            self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'data for send_privmsg is missing `channel` key'})
            return

        if 'message' not in data:
            self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'data for send_privmsg is missing `message` key'})
            return

        channel = data['channel'].lower().strip()
        if channel not in channels:
            self.write_json(type=_RequestType.CHANNEL_NOT_FOUND, data={'reason': f'bot is not in requested channel `{channel}`'})
            return

        await channels[channel].send_message(data['message'])
        self.write_json(type=_RequestType.SUCCESS, data={'type': _RequestType.SEND_PRIVMSG})

    async def run(self):
        try:
            if cfg.command_server_password.strip():
                self.write_json(type=_RequestType.SEND_PASSWORD, data={})
                password = await self.read()
                if password != cfg.command_server_password.strip():
                    self.write_json(type=_RequestType.BAD_PASSWORD, data={})
                    self.write_json(type=_RequestType.DISCONNECTING, data={})
                    return

            self.write_json(type=_RequestType.AUTHENTICATION_SUCCESSFUL, data={})
            self.write_json(type=_RequestType.LIST_CHANNELS, data={'channels': [channel.name for channel in channels.values()]})

            while self._running:
                try:
                    data = json.loads(await self.read())
                except (json.JSONDecodeError, TypeError):
                    self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'response must be valid json'})
                    continue

                if not isinstance(data, dict):
                    self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'data must be dictionary'})
                    continue

                if 'type' not in data:
                    self.write_json(type=_RequestType.BAD_DATA, data={'reason': 'data is must have the `type` key'})
                    continue

                msg_type = data['type']

                if msg_type == _RequestType.SEND_PRIVMSG:
                    await self.handle_send_privmsg(data)
        except ConnectionResetError:
            return


async def handle_client(reader: StreamReader, writer: StreamWriter):
    await ClientHandler(reader, writer).run()
