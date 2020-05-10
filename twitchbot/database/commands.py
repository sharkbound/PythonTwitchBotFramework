from typing import Optional, List

from .session import session
from .models import CustomCommand

__all__ = (
    'custom_command_exist',
    'get_custom_command',
    'add_custom_command',
    'delete_custom_command',
    'get_all_custom_commands',
)


def custom_command_exist(channel: str, name: str) -> bool:
    return bool(
        session.query(CustomCommand).filter(CustomCommand.channel == channel, CustomCommand.name == name).count())


def get_custom_command(channel: str, name: str) -> Optional[CustomCommand]:
    """gets a custom command from the DB, returns the command if found, else None"""
    assert isinstance(name, str), 'name must be of type str'
    return session.query(CustomCommand).filter(CustomCommand.channel == channel,
                                               CustomCommand.name == name).one_or_none()


def add_custom_command(cmd: CustomCommand) -> bool:
    """adds a custom command, returns a bool if it was successful"""

    if get_custom_command(cmd.channel, cmd.name) is not None:
        return False

    session.add(cmd)
    session.commit()
    return True


def delete_custom_command(channel: str, name: str) -> bool:
    """deletes the custom command from the DB if it exist, return if it was successful"""
    assert isinstance(name, str), 'name must be of type str'

    if get_custom_command(channel, name) is None:
        return False

    session.query(CustomCommand).filter(CustomCommand.channel == channel, CustomCommand.name == name).delete()
    session.commit()
    return True


def get_all_custom_commands(channel: str) -> List[CustomCommand]:
    return session.query(CustomCommand).filter(CustomCommand.channel == channel).all()
