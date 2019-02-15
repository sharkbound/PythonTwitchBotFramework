from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .command import Command


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
