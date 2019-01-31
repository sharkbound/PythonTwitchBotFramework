from pathlib import Path
from .config import Config

__all__ = ('cfg_disabled_mods', 'disable_mod', 'enable_mod', 'is_mod_disabled')


def _ensure_channel_data_exists(channel: str):
    if channel not in cfg_disabled_mods.data:
        cfg_disabled_mods[channel] = []


def is_mod_disabled(channel: str, mod: str):
    if channel not in cfg_disabled_mods.data:
        return False

    return mod in cfg_disabled_mods[channel]


def disable_mod(channel: str, mod: str):
    _ensure_channel_data_exists(channel)

    if mod not in cfg_disabled_mods[channel]:
        cfg_disabled_mods[channel].append(mod)
        cfg_disabled_mods.save()


def enable_mod(channel: str, mod: str):
    _ensure_channel_data_exists(channel)

    if mod not in cfg_disabled_mods[channel]:
        return

    cfg_disabled_mods[channel].remove(mod)
    cfg_disabled_mods.save()


cfg_disabled_mods = Config(Path('configs', 'disabled_mods.json'))
