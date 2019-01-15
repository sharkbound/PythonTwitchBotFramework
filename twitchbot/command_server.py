from asyncio import get_event_loop, start_server, StreamReader, StreamWriter
from .config import cfg
from .channel import channels, Channel

__all__ = 'start_command_server',

HOST = cfg.command_server_host
PORT = cfg.command_server_port
ENABLED = cfg.command_server_enabled


def start_command_server():
    if not ENABLED:
        return

    print(f'starting command server on {HOST}:{PORT}')
    get_event_loop().create_task(start_server(handle_client, HOST, PORT))


async def handle_client(reader: StreamReader, writer: StreamWriter):
    # helper function to read the next message from the client
    async def read():
        return (await reader.readline()).decode().strip()

    try:
        writer.write(b'Connected to the command server!\n')

        # wait for the client to select a valid channel to send messages
        channel_name = ''
        while channel_name not in channels:
            connected_channels = ', '.join(channels)
            writer.write(f'what channel do you want to join?\noptions: {connected_channels}\n'.encode())
            channel_name = await read()

        # client gave us a valid channel, now get the channel object from the cache
        channel: Channel = channels[channel_name]
        writer.write(b'Send `quit` to disconnect')

        # now we just relay messages send
        while True:
            msg = await read()
            if not msg or msg.lower() == 'quit':
                return

            await channel.send_message(msg)
    except ConnectionResetError:
        return
