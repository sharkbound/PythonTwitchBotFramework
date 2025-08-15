import os
import sys
import traceback
import typing

from asyncio import get_event_loop
from importlib import import_module
from inspect import isclass, getfile, getmodulename
from pathlib import Path
from traceback import print_exc
from typing import Dict, Callable, Any, Optional

if typing.TYPE_CHECKING:
    from .poll import PollData
    from .eventsub import EventSubMessage

from .channel import Channel
from .command import Command
from .config import cfg
from .disabled_mods import is_mod_disabled
from .enums import Event
from .events import trigger_event, AsyncEventWrapper
from .message import Message
from .shared import get_bot
from .util import temp_syspath, get_py_files, get_file_name, add_nameless_task
from .translations import translate

__all__ = ('ensure_mods_folder_exists', 'Mod', 'register_mod', 'trigger_mod_event', 'mods',
           'load_mods_from_directory', 'mod_exists', 'reload_mod', 'is_mod', 'unregister_mod',
           'ensure_commands_folder_exists', 'DEFAULT_MOD_NAME')

DEFAULT_MOD_NAME = 'DEFAULT'


# noinspection PyMethodMayBeStatic
class Mod:
    name = DEFAULT_MOD_NAME
    depends_on: typing.Collection[str] = ()

    @classmethod
    def name_or_class_name(cls):
        if cls.name == DEFAULT_MOD_NAME:
            return cls.__name__
        return cls.name

    async def loaded(self):
        """
        called when the Mod is loaded and created/registered
        """

    async def unloaded(self):
        """
        called when the Mod is unloaded (aka unregistered)
        """

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

    async def on_mod_reloaded(self, mod: 'Mod'):
        """
        triggered when a mod is reloaded using reload_mod() or !reloadmod
        :param mod: mod being reloaded
        """

    async def on_bot_banned_from_channel(self, msg: Message, channel: Channel):
        """
        triggered when the bot attempts to join a banned channel
        :param msg: the message that twitch sent saying the bot was banned
        :param channel: the channel the bot was banned from
        """

    async def on_bot_timed_out_from_channel(self, msg: Message, channel: Channel, seconds: int):
        """
        triggered when the bot is timed out on a channel
        :param msg: the message that twitch sent saying the bot was timed out
        :param channel: the channel the bot was timed out on
        :param seconds: how many seconds left in the timeout
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

    async def on_permission_check(self, msg: Message, cmd: Command) -> Optional[bool]:
        """
        triggered when a command permission check is requested
        :param msg: the message the command was found from
        :param cmd: the command that was found
        :return: bool indicating if the user has permission to call the command, True = yes, False = no
        """
        return None

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

    async def on_channel_raided(self, channel: Channel, raider: str, viewer_count: int):
        """
        triggered when the channel is raided
        :param channel: the channel who was raided
        :param raider: the user who raided
        :param viewer_count: the number of viewers who joined in the raid
        """

    async def on_channel_joined(self, channel: Channel):
        """
        triggered when the bot joins a channel
        """

    async def on_user_join(self, user: str, channel: Channel):
        """
        triggered when a user joins a channel the bot is in
        :param user: the user who joined
        :param channel: the channel that the user joined
        """

    async def on_user_part(self, user: str, channel: Channel):
        """
        triggered when a user leaves from a channel the bot is in
        :param user: the user who left
        :param channel: the channel that the user left
        """

    async def on_channel_subscription(self, subscriber: str, channel: Channel, msg: Message):
        """
        triggered when a user subscribes
        """

    async def on_channel_points_redemption(self, msg: Message, reward: str):
        """
        triggered when a viewers redeems channel points for a reward
        """

    async def on_poll_started(self, channel: Channel, poll: 'PollData'):
        """
        triggered when a bot poll starts from !startpoll command
        :param channel: channel the poll originated in
        :param poll: the poll that was started
        """

    async def on_poll_ended(self, channel: Channel, poll: 'PollData'):
        """
        triggered when a poll ends
        :param channel: channel the poll originated in
        :param poll: the poll that has ended
        """

    async def on_pubsub_received(self, raw: 'PubSubData'):
        """
        triggered when data is received from the pubsub client
        """

    async def on_pubsub_custom_channel_point_reward(self, raw: 'PubSubData', data: 'PubSubPointRedemption'):
        """
        triggered when a user redeems a channel's custom channel point reward
        :param raw: the raw pubsub message
        :param data: data specific to the custom channel point reward redeemed
        """

    async def on_raw_eventsub_received(self, data: 'EventSubMessage', channel_name: str):
        """
        Triggers when ANY eventsub message is received. This receives the raw EventSub message in a generic `EventSubMessage` object.
        """
        pass

    async def on_bot_shutdown(self):
        """
        triggered when the bot is shutdown
        """

    async def on_after_database_init(self):
        """
        triggered AFTER the bot creates all defined tables in the database
        this event should be used when you need to do database operations as soon as possible on bot startup
        """
    
    async def on_user_state(self, msg: 'Message'):
        """
        Triggered when twitch sends a USERSTATE update to the bot account
        
        Useful for tracking if the bot is a moderator or not (via 'moderator' badge)
        """
    async def on_room_state(self, msg: 'Message'):
        """
        Triggered when twitch sends a ROOMSTATE update to the bot account
        
        Tags:
            emote-only (0 = disabled)
            followers-only (-1 = disabled)
            r9k (0 = disabled)
            slow (0 = disabled)
            subs-only (0 = disabled)
            
        """

    # endregion


mods: Dict[str, Mod] = {}


def register_mod(mod: Mod) -> bool:
    """
    registers a mod globally
    :param mod: the mod to register
    :return: if registration was successful
    """
    if mod.name_or_class_name() in mods:
        return False

    mods[mod.name_or_class_name()] = mod
    add_nameless_task(mod.loaded())
    return True


def unregister_mod(mod: Mod) -> bool:
    """
    unregisters a mod from the global cache `mods`
    :param mod: mod to unregister
    :return: if it successfully unregistered it
    """
    if mod.name_or_class_name() not in mods:
        return False

    add_nameless_task(mod.unloaded())
    del mods[mod.name_or_class_name()]
    return True


async def trigger_mod_event(event: Event, *args, channel: str = '') -> list:
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
        if channel and is_mod_disabled(channel, mod.name_or_class_name()):
            continue

        try:
            output.append(await getattr(mod, event.value, _missing_function)(*args))
        except Exception as e:
            print(translate('mod_event_error', error=str(e), error_type=str(type(e)), mod_name=mod.name_or_class_name(), event=str(event)))
            traceback.print_exc()
    return output


def ensure_mods_folder_exists():
    """
    creates the mod folder if it does not exists
    """
    if not os.path.exists(cfg.mods_folder):
        os.mkdir(cfg.mods_folder)


def ensure_commands_folder_exists():
    """
    creates the commands folder if it does not exists
    """
    if not os.path.exists(cfg.commands_folder):
        os.mkdir(cfg.commands_folder)


def load_mods_from_directory(fullpath, predicate: Callable[[str, Any], bool] = None, log=True):
    """
    loads all mods from the given directory, only .py files are loaded
    :param fullpath: the path to search for mods to load
    """
    if log:
        print('loading mods from:', fullpath)

    found_mods = [
        mod
        for mod in iter_mods_from_directory(fullpath, predicate)
        if predicate is None or (predicate is not None and predicate(mod.name_or_class_name(), mod))
    ]

    dependency_map = {mod.name_or_class_name(): (mod, tuple(mod.depends_on)) for mod in found_mods}
    while dependency_map:
        loadable_mods = [mod for mod, deps in dependency_map.values() if not deps or all(dep in mods for dep in deps)]

        if not loadable_mods and dependency_map:
            show_mod_dependencies_error(dependency_map, fullpath)
            return

        for mod in loadable_mods:
            register_mod(mod())
            del dependency_map[mod.name_or_class_name()]


def show_mod_dependencies_error(dependency_map, fullpath):
    gentabs = lambda count: '\n' + '\t' * count
    all_deps = [dep for _, deps in dependency_map.values() for dep in deps]
    all_missing_deps = set(dep for dep in all_deps if dep not in mods and dep not in dependency_map)
    print(f'\n{"MOD DEPENDENCY ERROR":=^50}')
    print(f'Mod directory that was trying to load: {fullpath}\n')
    print(
        f'Cannot load mods:\n\t{gentabs(1).join(dependency_map)}\n\nBecause of missing mod dependencies:\n\t{gentabs(1).join(all_missing_deps)}')
    mods_missing_deps = []
    for mod, deps in dependency_map.values():
        missing = set(deps) & all_missing_deps
        if not missing:
            continue
        mods_missing_deps.append(
            f'{mod.name_or_class_name()} is missing these mod dependencies:\n\t\t{gentabs(2).join(missing)}\n')
    missing_deps_breakdown = '\n\t'.join(mods_missing_deps)
    print(f'\nBreakdown of missing mod dependencies:\n\t{missing_deps_breakdown}')
    print('=' * 50 + '\n')
    return


def iter_mods_from_directory(fullpath, predicate: Callable[[str, Any], bool] = None):
    """
    iterates through all mod classes from the given directory, only .py files are loaded
    :param fullpath: the path to search for mods to load
    """
    with temp_syspath(fullpath):
        for file in get_py_files(fullpath):
            # we need to import the module to get its attributes
            module = import_module(get_file_name(file))
            for obj in module.__dict__.values():
                # verify the obj is a class, is a subclass of Mod, and is not Mod class itself
                if not is_mod(obj):
                    continue
                if predicate is None or (predicate is not None and predicate(obj.name_or_class_name(), obj)):
                    yield obj




def reload_mod(mod_name: str):
    mod = mods.get(mod_name)
    if mod is None:
        raise ValueError(f'could not find mod by the name of "{mod_name}"')

    try:
        # get the module's file path, this is needed to add it to python's import search paths
        path = Path(getfile(mod.__class__))
        with temp_syspath(path.parent):
            # this is needed to make python import the latest version from disk,
            # python caches imports in sys.modules
            # doing this removes it from the cache, so the latest version from the disk is imported
            prev_module = sys.modules[getmodulename(path)]
            del sys.modules[getmodulename(path)]
            # this dict stores the Mod's / global objects in the Mod's .py file
            # it lets us iterate over its value to check for the Mod that we want to reload
            module = __import__(getmodulename(path), locals={}, globals={})
            for item in module.__dict__.values():
                if is_mod(item) and item.name_or_class_name() == mod.name_or_class_name():
                    unregister_mod(mod)
                    reloaded_mod = item()
                    register_mod(reloaded_mod)

                    # removed previous events that were registered via @event_handler
                    # this prevents event duplication and stacking
                    for var in prev_module.__dict__.values():
                        if isinstance(var, AsyncEventWrapper):
                            var.unregister()

                    # trigger events
                    add_nameless_task(trigger_mod_event(Event.on_mod_reloaded, reloaded_mod))
                    add_nameless_task(get_bot().on_mod_reloaded(reloaded_mod))
                    add_nameless_task(trigger_event(Event.on_mod_reloaded, reloaded_mod))
                    return True

    except Exception as e:
        print(f'error trying to reload Mod "{mod.name_or_class_name()}", error type: {type(e)}, error: {e}')
        print_exc()
    return False


def is_mod(obj):
    return isclass(obj) and issubclass(obj, Mod) and obj is not Mod


def mod_exists(mod: str) -> bool:
    """
    returns of a mod exists
    :param mod: the mod to check for
    :return: bool indicating if the mod exists
    """
    return mod in mods
