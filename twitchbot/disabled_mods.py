from pathlib import Path
from .config import Config
from asyncio import get_event_loop

__all__ = ('cfg_disabled_mods', 'disable_mod', 'enable_mod', 'is_mod_disabled')


def _ensure_channel_data_exists(channel: str):
    """
    creates a channel's config data if it does not exist
    :param channel: the channel to verify data exist for
    """
    if channel not in cfg_disabled_mods.data:
        cfg_disabled_mods[channel] = []


def is_mod_disabled(channel: str, mod: str) -> bool:
    """
    checks if a mod is disabled for a channel
    :param channel: the channel to check for if the mod is disabled in
    :param mod: the mod to check if it is disabled for the channel
    :return: bool indicating if the mod is disabled for the channel
    """
    if channel not in cfg_disabled_mods.data:
        return False

    return mod in cfg_disabled_mods[channel]


def disable_mod(channel: str, mod: str):
    """
    disables a mod for the given channel
    :param channel: the channel to disable the mod for
    :param mod: the mod to disable for the channel
    """
    # "hack" to avoid circular import
    from .modloader import mods

    _ensure_channel_data_exists(channel)

    if mod not in cfg_disabled_mods[channel]:
        cfg_disabled_mods[channel].append(mod)
        cfg_disabled_mods.save()

    get_event_loop().create_task(mods[mod].on_disable(channel))


def enable_mod(channel: str, mod: str):
    """
    enables a mod for the given channel
    :param channel: channel to enable the mod for
    :param mod: the mod to enable for the channel
    """
    # "hack" to avoid circular import
    from .modloader import mods

    _ensure_channel_data_exists(channel)

    if mod not in cfg_disabled_mods[channel]:
        return

    cfg_disabled_mods[channel].remove(mod)
    cfg_disabled_mods.save()
    get_event_loop().create_task(mods[mod].on_enable(channel))


cfg_disabled_mods = Config(Path('configs', 'disabled_mods.json'))
