from typing import TYPE_CHECKING
from .translations import translate

if TYPE_CHECKING:
    from .command import Command

__all__ = [
    'BotNotRunningError',
    'InvalidArgumentsError',
    'BadTwitchAPIResponse',
]


class BotNotRunningError(Exception): pass


class InvalidArgumentsError(Exception):
    """
    used to trigger a command's help message in twitch chat when caller gives the command invalid arguments
    """

    # this is a default for if the class is raised without calling its init, ex: raise InvalidArgumentsError
    reason: str = 'invalid arguments'
    cmd: 'Command' = None

    def __init__(self, reason: str = reason, cmd: 'Command' = None):
        super().__init__(reason)
        self.cmd: 'Command' = cmd
        self.reason: str = reason


class BadTwitchAPIResponse(Exception):
    def __init__(self, endpoint, message):
        super().__init__(translate('bad_twitch_api_response', message=message, endpoint=endpoint))
