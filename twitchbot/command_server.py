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


async def handle_client(reader: StreamReader, writer: StreamWriter):
    # helper function to read the next message from the client
    async def read():
        return (await reader.readline()).decode('utf8').strip()

    def write_json(**data):
        writer.write(json.dumps(data).encode())

    try:
        if cfg.command_server_password.strip():
            write_json(type=_RequestType.SEND_PASSWORD, data={})
            password = await read()
            if password != cfg.command_server_password.strip():
                write_json(type=_RequestType.BAD_PASSWORD, data={})
                write_json(type=_RequestType.DISCONNECTING, data={})
                return

        write_json(type=_RequestType.LIST_CHANNELS, data={'channels': [channel.name for channel in channels.values()]})
        while True:
            try:
                data = json.loads(await read())
                print(f'data: {data}')
            except (json.JSONDecodeError, TypeError):
                write_json(type=_RequestType.BAD_DATA, data={'reason': 'response must be valid json'})


    except ConnectionResetError:
        return

# async def handle_client(reader: StreamReader, writer: StreamWriter):
#     # helper function to read the next message from the client
#     async def read():
#         return (await reader.readline()).decode('utf8').strip()
#
#     try:
#         writer.write(b'Connected to the command server!\n')
#
#         # wait for the client to select a valid channel to send messages
#         channel_name = ''
#         while channel_name not in channels:
#             connected_channels = ', '.join(channels)
#             writer.write(f'what channel do you want to join?\noptions: {connected_channels}\n'.encode())
#             channel_name = await read()
#
#         # client gave us a valid channel, now get the channel object from the cache
#         channel: Channel = channels[channel_name]
#         writer.write(b'Send `quit` to disconnect')
#
#         # now we just relay messages send
#         while True:
#             msg = await read()
#             if not msg or msg.lower() == 'quit':
#                 return
#
#             await channel.send_message(msg)
#     except ConnectionResetError:
#         return
