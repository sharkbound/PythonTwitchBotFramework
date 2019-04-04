import os
import traceback
from inspect import isclass

from typing import Dict
from .util import temp_syspath, get_py_files, get_file_name
from .channel import Channel
from .command import Command
from .config import cfg
from .enums import Event
from .message import Message
from .disabled_mods import is_mod_disabled
from importlib import import_module

__all__ = ('ensure_mods_folder_exists', 'Mod', 'register_mod', 'trigger_mod_event', 'mods',
           'load_mods_from_directory', 'mod_exists')


# noinspection PyMethodMayBeStatic
class Mod:
    name = 'DEFAULT'

    # region events
    async def on_enable(self, channel: str):
        """
        triggered when the mod is enabled
        :param channel: the channel the mod is enabled in
        """

    async def on_disable(self, channel: str):
        """
        triggered when the mod is disabled
        :param channel: the channel the mod is disabled in
        """

    async def on_connected(self):
        """
        triggered when the bot connects to all the channels specified in the config file
        """

    async def on_raw_message(self, msg: Message):
        """
        triggered the instant a message is received,
        this message can be any message received,
        including twitches messages that do not have any useful information
        """

    async def on_privmsg_sent(self, msg: str, channel: str, sender: str):
        """
        triggered when the bot sends a privmsg
        """

    async def on_privmsg_received(self, msg: Message):
        """
        triggered when a privmsg is received, is not triggered if the msg is a command
        """

    async def on_whisper_sent(self, msg: str, receiver: str, sender: str):
        """
        triggered when the bot sends a whisper to someone
        """

    async def on_whisper_received(self, msg: Message):
        """
        triggered when a user sends the bot a whisper
        """

    async def on_permission_check(self, msg: Message, cmd: Command) -> bool:
        """
        triggered when a command permission check is requested
        :param msg: the message the command was found from
        :param cmd: the command that was found
        :return: bool indicating if the user has permission to call the command, True = yes, False = no
        """
        return True

    async def on_before_command_execute(self, msg: Message, cmd: Command) -> bool:
        """
        triggered before a command is executed
        :return bool, if return value is False, then the command will not be executed
        """
        return True

    async def on_after_command_execute(self, msg: Message, cmd: Command):
        """
        triggered after a command has executed
        """

    async def on_bits_donated(self, msg: Message, bits: int):
        """
        triggered when a bit donation is posted in chat
        """

    async def on_channel_joined(self, channel: Channel):
        """
        triggered when the bot joins a channel
        """

    async def on_channel_subscription(self, channel: Channel, msg: Message):
        """
        triggered when a user subscribes
        """

    # endregion


mods: Dict[str, Mod] = {}


def register_mod(mod: Mod) -> bool:
    """
    registers a mod globally
    :param mod: the mod to register
    :return: if registration was successful
    """
    if mod.name in mods:
        return False

    mods[mod.name] = mod
    return True


async def trigger_mod_event(event: Event, *args, channel: str = None) -> list:
    """
    triggers a event on all mods
    if the channel is passed, the it is checked if the mod is enabled for that channel,
    if not, the event for that mod is skipped
    :param event: the event to raise on all the mods
    :param args: the args to pass to the event
    :param channel: the channel the event is being raised from
    :return: the result of all the mod event calls in a list
    """

    async def _missing_function(*ignored):
        pass

    output = []
    for mod in mods.values():
        if channel and is_mod_disabled(channel, mod.name):
            continue

        try:
            output.append(await getattr(mod, event.value, _missing_function)(*args))
        except Exception as e:
            print(f'\nerror has occurred while triggering a event on a mod, details:\n'
                  f'mod: {mod.name}\n'
                  f'event: {event}\n'
                  f'error: {type(e)}\n'
                  f'reason: {e}\n'
                  f'stack trace:')
            traceback.print_exc()
    return output


def ensure_mods_folder_exists():
    """
    creates the mod folder if it does not exists
    """
    if not os.path.exists(cfg.mods_folder):
        os.mkdir(cfg.mods_folder)


def load_mods_from_directory(fullpath):
    """
    loads all mods from the given directory, only .py files are loaded
    :param fullpath: the path to search for mods to load
    """

    print('loading mods from:', fullpath)

    with temp_syspath(fullpath):
        for file in get_py_files(fullpath):
            # we need to import the module to get its attributes
            module = import_module(get_file_name(file))
            for obj in module.__dict__.values():
                # verify the obj is a class, is a subclass of Mod, and is not Mod class itself
                if not isclass(obj) or not issubclass(obj, Mod) or obj is Mod:
                    continue
                # create a instance of the mod subclass, then register it
                register_mod(obj())


def mod_exists(mod: str) -> bool:
    """
    returns of a mod exists
    :param mod: the mod to check for
    :return: bool indicating if the mod exists
    """
    return mod in mods
