#!/usr/bin/env python3
import asyncio
import json

import click
import websockets
from urwid import AsyncioEventLoop, Edit, Filler, Frame, MainLoop, Text, connect_signal
COMMAND_READ, PASSWORD_READ = 0, 1

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

loop = asyncio.get_event_loop()


@click.command()
@click.option('--host', prompt='Command server host', default='localhost')
@click.option('--port', prompt='Command server port', default='1337')
def run(host, port):
    """
    Start a websocket client and a terminal UI to interact with it.
    """
    # connection state
    channels = []
    bound_channel = None
    ws = None

    # UI state
    lines = ['example text\n']
    output = Text(lines)
    input_field = Edit('>> ')
    input_state = COMMAND_READ
    widget = Frame(Filler(output, 'top'), footer=input_field)
    widget.focus_position = 'footer'

    # event wiring
    event_loop = AsyncioEventLoop(loop=loop)
    input_cb = None

    def write(msg):
        """
        Show an additional line of text.
        """
        lines.append(msg + '\n')
        output.set_text(lines)

    def prompt_for_password(msg):
        """
        Change prompt to password prompt. Return a future for the typed password.
        """
        nonlocal input_cb, input_state
        input_cb = loop.create_future()
        input_state = PASSWORD_READ
        input_cb.add_done_callback(_password_done)
        input_field.set_mask('*')
        input_field.set_caption(msg)
        return input_cb

    def _password_done(_):
        nonlocal input_state
        input_field.set_mask(None)
        input_state = COMMAND_READ

    def accept_input(key):
        """
        Process typed lines of text. Dispatches to password prompt or command prompt
        as needed.
        """
        if key == 'enter':
            if input_state == PASSWORD_READ:
                input_cb.set_result(input_field.edit_text)
            elif input_state == COMMAND_READ:
                cmd_dispatch(input_field.edit_text)
            input_field.set_edit_text('')

    def update_channels(new_channels):
        """
        Receive channel data.
        """
        nonlocal channels, bound_channel
        channels = new_channels
        if len(channels) == 1:
            bound_channel = channels[0]
            write(f'bound console to channel "{bound_channel}"')
        else:
            write(f'bot is in these channels: {", ".join(channels)}')

    async def ws_dispatch():
        """
        Handle websocket messages.
        """
        nonlocal ws
        ws = await websockets.connect(f'ws://{host}:{port}')
        while True:
            try:
                msg = json.loads(await p.recv())
                if msg['type'] == SEND_PASSWORD:
                    p.send(await prompt_for_password("Server password:"))
                elif msg['type'] == DISCONNECTING:
                    write('server terminated connection...')
                    ws = None
                elif msg['type'] == BAD_PASSWORD:
                    write('authentication failed... password did not match!')
                elif msg['type'] == LIST_CHANNELS:
                    update_channels(msg['data']['channels'])
                elif msg['type'] == AUTHENTICATION_SUCCESSFUL:
                    write('logged into command server!')

            except Exception as e:
                write(f'Error: {e}')

    def print_help():
        write('/channel <channel> : binds this console to a bot-joined channel (needed for /chat)')
        write('/chat <msg> : sends the chat message to the channel bound to this console')
        write('/sendcmd <commands> [args...]: tells the bot run a command')
        write('/help to see this message again')

    def cmd_dispatch(command):
        nonlocal bound_channel
        if not ws:
            write('Not connected')
            return
        parts = command.split()

        if not parts:
            print_help()

        command_part = parts[0].lower()
        args = parts[1:]
        if command_part == 'help':
            print_help()
        elif command_part == 'sendcmd':
            if not bound_channel:
                write('there is not a bound channel! use `/channel <channel>` to bind one!')
            elif not args:
                    write('you must provide a command to run to /sendcmd, ex: /sendcmd help')
            else:
                return ws.send(
                    json.dumps(
                        {
                            'type': RUN_COMMAND,
                            'channel': bound_channel,
                            'command': args[0],
                            'args': args[1:],
                            'silent': True,
                        }
                    )
                )
        elif command_part == 'chat':
            if not bound_channel:
                write('there is not a bound channel! use `/channel <channel>` to bind one!')
            else:
                return ws.send(
                    json.dumps(
                        {
                            'type': SEND_PRIVMSG,
                            'channel': bound_channel,
                            'message': ' '.join(args),
                        }
                    )
                )

        elif command_part == 'channel':
            if not channels:
                write('the bot is not currently in any channels, please have the bot join at least one than relaunch this console')
            elif not args:
                write(f'the bot is currently in these channels: {", ".join(channels)}\ndo `/channel <channel>` to bind this channel to one')
            elif args[0] not in channels:
                write(f'the bot is not currently in "{args[0]}"')
            else:
                bound_channel = args[0]

    event_loop.alarm(0, lambda: loop.create_task(ws_dispatch()))
    MainLoop(widget, event_loop=event_loop, unhandled_input=accept_input).run()



if __name__ == '__main__':
    run()
