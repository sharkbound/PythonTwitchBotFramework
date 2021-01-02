import asyncio
import getpass
import json
from functools import partial
from typing import Optional, List, Coroutine

import websockets


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
    RUN_COMMAND = 'run_command'


class State:
    def __init__(self):
        self.bound_channel = ''
        self.channels: List[str] = []
        self.authenticated = False
        self.reads_left = 0

    @property
    def waiting_for_read(self):
        return self.reads_left > 0

    @property
    def has_bound_channel(self):
        return bool(self.bound_channel)


def print_help():
    print('/channel <channel> : binds this console to a bot-joined channel (needed for /chat)')
    print('/chat <msg> : sends the chat message to the channel bound to this console')
    print('/sendcmd <commands> [args...]: tells the bot run a command')
    print('/help to see this message again')


async def run():
    host = input('enter command server host (leave blank for "localhost"): ').strip() or 'localhost'
    port = int(input('enter command server port (leave blank for 1337): ').strip() or 1337)
    connection = Connection(host, port)

    await connection.connect()
    state = State()

    while True:
        data = await connection.read_json()
        if state.reads_left > 0:
            state.reads_left -= 1
        msg_type = data['type']

        if msg_type == _RequestType.SEND_PASSWORD:
            await connection.send(getpass.getpass('enter password for server >>> ').strip())

        elif msg_type == _RequestType.DISCONNECTING:
            print('server terminated connection...')
            return

        elif msg_type == _RequestType.BAD_PASSWORD:
            print('authentication failed... password did not match!')
            return

        elif msg_type == _RequestType.LIST_CHANNELS:
            await update_state_channels(data, state)

        elif msg_type == _RequestType.AUTHENTICATION_SUCCESSFUL:
            state.authenticated = True
            state.reads_left += 1
            print('logged in to command server!')
            print_help()

        while state.authenticated and not state.waiting_for_read:
            command = input('>> ')
            parts = command.split()

            if not parts:
                print_help()
                continue

            command_part = parts[0].lower()
            if command_part in client_commands:
                await client_commands[command_part](connection, state, parts[1:])


async def update_state_channels(data, state):
    state.channels = data['data']['channels']
    if len(state.channels) == 1:
        state.bound_channel = state.channels[0]
        print(f'bound console to channel "{state.bound_channel}"')
    else:
        print(f'bot is in these channels: {", ".join(state.channels)}')


client_commands = {}


def client_command(func: Coroutine = None, name: str = '', prefix: str = '/'):
    if func is None:
        return partial(client_command, name=name, prefix=prefix)

    client_commands[prefix + name] = func
    return func


@client_command(name='help')
async def c_help(connection: Connection, state: State, args: List[str]):
    print_help()


@client_command(name='sendcmd')
async def c_sendcmd(connection: Connection, state: State, args: List[str]):
    if not state.has_bound_channel:
        print('there is not a bound channel! use `/channel <channel>` to bind one!')
        return

    if not args:
        print('you must provide a command to run to /sendcmd, ex: /sendcmd help')
        return

    state.reads_left += 1
    await connection.send_json(type=_RequestType.RUN_COMMAND, channel=state.bound_channel, command=args[0], args=args[1:], silent=True)


@client_command(name='chat')
async def c_chat(connection: Connection, state: State, args: List[str]):
    if not args:
        print('you must provide a message after /chat, ex: `/chat hello chat!`')
        return

    if not state.has_bound_channel:
        print('there is not a bound channel! use `/channel <channel>` to bind one!')
        return

    state.reads_left += 1
    await connection.send_json(type=_RequestType.SEND_PRIVMSG, channel=state.bound_channel, message=' '.join(args))


@client_command(name='channel')
async def c_channel(connection: Connection, state: State, args: List[str]):
    if not state.channels:
        print('the bot is not currently in any channels, please have the bot join at least one than relaunch this console')
        return

    if not args:
        print(f'the bot is currently in these channels: {", ".join(state.channels)}\ndo `/channel <channel>` to bind this channel to one')
        return

    if args[0] not in state.channels:
        print(f'the bot is not currently in "{args[0]}"')
        return

    state.bound_channel = args[0]


if __name__ == '__main__':
    asyncio.run(run())
