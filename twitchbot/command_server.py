import json
from typing import Optional, Callable, Awaitable

import websockets
from traceback import format_exc
from functools import partial

from .channel import channels
from .config import cfg
from .exceptions import InvalidArgumentsError
from .command import get_command
from .translations import translate

__all__ = [
    'start_command_server',
    'stop_command_server',
    'CommandServerMessage'
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
    SEND_WHISPER = 'send_whisper'
    CHANNEL_NOT_FOUND = 'channel_not_found'
    SUCCESS = 'success'
    RUN_COMMAND = 'run_command'
    DISCONNECT = 'disconnect'


from .message import Message


class CommandServerMessage(Message):
    def __init__(
            self,
            msg,
            irc=None,
            bot=None,
            silent: bool = False,
            echo_response: bool = False,
            websocket: websockets.WebSocketServerProtocol = None,
            custom_data: dict = None,
            output: list = None,
    ):
        super().__init__(msg, irc, bot)
        self.websocket = websocket
        self.silent = silent
        self.echo_response = echo_response
        self.custom_data = custom_data or {}
        self.output = output

    async def reply(self, msg: str = '', whisper=False, strip_command_prefix: bool = True, as_twitch_reply: bool = False):
        if self.silent:
            print(f'COMMAND SERVER [SILENT RUN OUTPUT]: {msg}')
        else:
            await super().reply(msg=msg, whisper=whisper, strip_command_prefix=strip_command_prefix, as_twitch_reply=as_twitch_reply)

        if self.echo_response and isinstance(self.output, list):
            self.output.append(msg)

    # noinspection PyUnresolvedReferences
    async def wait_for_reply(self, predicate: Callable[['Message'], Awaitable[bool]] = None, timeout=30, default=None,
                             raise_on_timeout=False) -> 'ReplyResult':
        raise RuntimeError(f'wait_for_reply() is not supported on CommandServer sent messages')


class ClientHandler:
    def __init__(self, websocket: websockets.WebSocketServerProtocol, path: str):
        self.path = path
        self.websocket = websocket
        self._running = True

    async def read(self):
        return (await self.websocket.recv()).strip()

    async def write_json_preserve_custom_data(self, *, original_data, **kwargs):
        await self.write_json(
            **kwargs,
            custom_data=original_data.get('custom_data')
        )

    async def write_json(self, **data):
        await self.websocket.send(f'{json.dumps(data)}')

    async def handle_send_privmsg(self, data: dict):
        if 'channel' not in data:
            await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.BAD_DATA,
                                                       data={'reason': 'data for send_privmsg is missing `channel` key'})
            return

        if 'message' not in data:
            await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.BAD_DATA,
                                                       data={'reason': 'data for send_privmsg is missing `message` key'})
            return

        channel = data['channel'].lower().strip()
        if channel not in channels:
            await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.CHANNEL_NOT_FOUND,
                                                       data={'reason': f'bot is not in requested channel `{channel}`'})
            return

        await channels[channel].send_message(data['message'])
        await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.SUCCESS, data={'type': _RequestType.SEND_PRIVMSG})

    async def handle_send_whisper(self, data: dict):
        for key in ('user', 'message'):
            if key not in data:
                await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.BAD_DATA,
                                                           data={'reason': f'data for send_whisper is missing `{key}` key'})
                return
        from twitchbot import get_bot
        await get_bot().irc.send_whisper(data['user'], data['message'])
        await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.SUCCESS, data={'type': _RequestType.SEND_WHISPER})

    async def _guard_run_cmd(self, data: dict):
        from .util import run_command, join_args_to_original_string
        from .irc import create_fake_privmsg

        output = []
        silent = data.get('silent', False)
        echo_response = data.get('echo_response', False)
        try:
            msg_class = CommandServerMessage if silent else None
            await run_command(
                name=data['command'],
                msg=create_fake_privmsg(data['channel'], ''),
                args=list(data['args']),
                blocking=True,
                msg_class=partial(msg_class, silent=silent, echo_response=echo_response, websocket=self.websocket, output=output)
            )
        except InvalidArgumentsError as e:
            command = get_command(data['command'])
            if command is not None:
                usage = translate('command_server_proper_command_syntax', cmd_syntax=command.syntax)
            else:
                usage = ''
            if echo_response:
                output.append(
                    # f'attempt to run command "{data["command"]}" with args {data["args"]} raised a error. {usage}details:\n\t{e.__class__.__name__}: {e}',
                    # f'attempt to run command "{command}" with args {args} raised a error. {usage}details:\n\t{error_type}: {error}',
                    translate(
                        'command_server_invalid_arguments_error_response',
                        command=data['command'],
                        args=str(data['args']),
                        usage=usage,
                        error=str(e),
                        error_type=str(type(e)),
                        cmd_syntax=command.syntax,
                        reason=e.reason,
                        stack_trace=format_exc(),
                        joined_args=join_args_to_original_string(data['args']),
                    )
                )

        except Exception as e:
            formatted_error = translate(
                'command_server_error_executing_command',
                command=data['command'],
                args=data['args'],
                error_type=str(type(e)),
                error=str(e),
                stack_trace=format_exc(),
                joined_args=join_args_to_original_string(data['args']),
            )
            if echo_response:
                output.append(formatted_error)
            print(formatted_error)

        return output

    async def handle_run_command(self, data: dict):
        if 'channel' not in data:
            await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.BAD_DATA,
                                                       data={'reason': 'data for run_command is missing `channel` key'})
            return

        if 'command' not in data:
            await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.BAD_DATA,
                                                       data={'reason': 'data for run_command is missing `command` key'})
            return

        if 'args' not in data:
            await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.BAD_DATA,
                                                       data={'reason': 'data for run_command is missing `args` key'})
            return

        if not isinstance(data['args'], list):
            await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.BAD_DATA,
                                                       data={'reason': 'key `args` must be a list for `run_command`'})
            return

        # get_event_loop().create_task(self._guard_run_cmd(data, output=cmd_output))
        cmd_output = await self._guard_run_cmd(data)
        await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.SUCCESS,
                                                   data={'type': _RequestType.RUN_COMMAND, 'output': cmd_output, 'args': data['args'],
                                                         'command': data['command']})

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
                    await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.BAD_DATA,
                                                               data={'reason': 'data must be dictionary'})
                    continue

                if 'type' not in data:
                    await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.BAD_DATA,
                                                               data={'reason': 'data is missing key `type`'})
                    continue

                msg_type = data['type']

                if msg_type == _RequestType.SEND_PRIVMSG:
                    await self.handle_send_privmsg(data)
                elif msg_type == _RequestType.RUN_COMMAND:
                    await self.handle_run_command(data)
                elif msg_type == _RequestType.SEND_WHISPER:
                    await self.handle_send_whisper(data)
                elif msg_type == _RequestType.DISCONNECT:
                    await self.write_json_preserve_custom_data(original_data=data, type=_RequestType.DISCONNECTING)
                    await self.websocket.close()
                    return

        except ConnectionResetError:
            return

        except websockets.exceptions.ConnectionClosedOK:
            return


async def handle_client(websocket: websockets.WebSocketServerProtocol, path: str):
    await ClientHandler(websocket, path).run()
