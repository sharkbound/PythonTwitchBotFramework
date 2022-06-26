from pathlib import Path

from .config import Config

__all__ = ['TRANSLATIONS_DIRECTORY', 'get_translation', 'load_translation_file', 'translate', 'load_fallback_translation_file']

TRANSLATIONS_DIRECTORY = Path("translations")

_fallback_translations_config = Config(TRANSLATIONS_DIRECTORY / 'en_us.json')
_translations_config = Config(TRANSLATIONS_DIRECTORY / 'en_us.json')


def get_translation(key):
    if key in _translations_config:
        return _translations_config[key]

    if key in _fallback_translations_config:
        return _fallback_translations_config[key]

    raise ValueError(f'Translation not found: "{key}"')


def _ensure_json_extension(file):
    if not file.endswith('.json'):
        file += '.json'
    return file


def _load_translation_file(translation_file_name):
    path = TRANSLATIONS_DIRECTORY / _ensure_json_extension(translation_file_name)
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
