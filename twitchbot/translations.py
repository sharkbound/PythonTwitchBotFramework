from pathlib import Path

from .config import Config
from .bot_package_path import get_bot_package_path

__all__ = [
    'get_translation',
    'load_translation_file',
    'translate',
    'load_fallback_translation_file',
    'create_translate_callable',
]

_BUILTIN_TRANSLATION_DIRECTORY = get_bot_package_path() / 'builtin_translations'

_fallback_translations_config = Config(_BUILTIN_TRANSLATION_DIRECTORY / 'en_us.json')
_translations_config = Config(_BUILTIN_TRANSLATION_DIRECTORY / 'en_us.json')


def get_translation(key):
    if key in _translations_config:
        return _translations_config[key]

    if key in _fallback_translations_config:
        return _fallback_translations_config[key]

    # raise ValueError(f'Translation not found: "{key}"') # disabled for time being because of key errors when they should not happen
    return f'<TRANSLATION "{key}" NOT FOUND>'


def _ensure_json_extension(file):
    file = str(file)
    if not file.endswith('.json'):
        file += '.json'
    return Path(file)


def _ensure_is_pathlib(path):
    if not isinstance(path, Path):
        return Path(path)
    return path


def _load_translation_file(translation_file_location):
    path = _ensure_json_extension(_ensure_is_pathlib(translation_file_location))
    if not path.exists():
        raise ValueError(f'Tried to load non-existent translations file: "{path}"')
    return Config(path)


def load_fallback_translation_file(translation_file_name):
    global _fallback_translations_config
    _fallback_translations_config = _load_translation_file(translation_file_name)


def load_translation_file(translation_file_name):
    global _translations_config
    _translations_config = _load_translation_file(translation_file_name)


def translate(key, *args, **kwargs):
    return get_translation(key).format(*args, **kwargs)


def create_translate_callable(translation_key: str, *args, **kwargs):
    """Create a callable object for the given translation key."""
    return lambda: translate(translation_key, *args, **kwargs)
