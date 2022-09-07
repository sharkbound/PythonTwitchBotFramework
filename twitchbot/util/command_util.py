import re
from asyncio import get_event_loop
from typing import List, TYPE_CHECKING, Type, Union, Callable, Any, Optional
from ..exceptions import InvalidArgumentsError

if TYPE_CHECKING:
    from ..message import Message
    from ..command import Command

__all__ = [
    'run_command',
    'strip_twitch_command_prefix',
    'RE_TWITCH_COMMAND_PREFIX',
    'raise_invalid_arguments_error_if_falsy'
]


async def run_command(name: str, msg: 'Message', args: List[str] = None, blocking: bool = True, msg_class: Type['Message'] = None):
    """
    runs a command from another command, can be used for chaining command pragmatically,
    the base message passed to this function MUST be a WHISPER or PRIVMSG for this to work

    example (called from another command)

    >>> # `msg` is from the first command triggered from the actual chat from the channel
    >>> # ['17'] is the arguments passed to this newly command, can be empty
    >>> await run_command('roll', msg, ['17'])

    :param name: the name of the command to call, if the name is not found, it tries it with the prefix added
    :param msg: the message instance of first command called, needed to retain state, and keep natural flow
    :param args: the arguments to pass to the newly called command
    :param blocking: if True, the caller will wait for newly called command to be done before continuing,
                     else, run it as another task and continue
    """
    from twitchbot import Message, get_command, get_custom_command, Command, CustomCommand, CustomCommandAction

    cmd: Command = get_command(name) or get_custom_command(msg.channel_name, name)
    if not cmd:
        raise ValueError(f'[run_command] could not find command or custom command by the name of "{name}"')
    if isinstance(cmd, CustomCommand):
        cmd = CustomCommandAction(cmd)

    args = [f'"{arg}"' if ' ' in arg else arg for arg in (args or [])]
    raw = msg.raw_msg
    # get the original info line from the twitch message, then append our new arguments to it to be parsed
    # the consecutive raw.index(':') is used to skip the first two ':' in the original message
    # we want to preserve all metadata/info prior to the last : before the actual message contents
    text = raw[:raw.index(':', raw.index(':') + 1) + 1]
    # create a new message from the formatted new raw text, this is needed to ensure everything flows as intended
    # here the base message data is used, then we replace the context with our own command and arguments
    new_msg = (Message if msg_class is None else msg_class)(f"{text}{cmd.fullname} {' '.join(args)}", irc=msg.irc, bot=msg.bot)

    if blocking:
        await cmd.execute(new_msg)
    else:
        get_event_loop().create_task(cmd.execute(new_msg))


RE_TWITCH_COMMAND_PREFIX = re.compile(r'^[./]+')


def strip_twitch_command_prefix(string: str) -> str:
    return RE_TWITCH_COMMAND_PREFIX.sub('', string)


def raise_invalid_arguments_error_if_falsy(value, message: Union[str, Callable[[Any], str]], cmd: Optional['Command'] = None):
    if value:
        return

    if isinstance(message, str):
        raise InvalidArgumentsError(reason=message, cmd=cmd)
    else:
        raise InvalidArgumentsError(reason=message(value), cmd=cmd)
