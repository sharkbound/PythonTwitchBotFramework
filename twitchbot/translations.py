from .config import CONFIG_FOLDER, Config

__all__ = ['TRANSLATIONS_DIRECTORY', 'get_translation', 'load_translation_file', 'translate', 'translations_config']

TRANSLATIONS_DIRECTORY = CONFIG_FOLDER / "translations"
translations_config = Config(TRANSLATIONS_DIRECTORY / 'en_us.json')


def get_translation(self, key):
    return self.translations_config[key]


def _ensure_json_extension(file):
    if not file.endswith('.json'):
        file += '.json'
    return file


def load_translation_file(translation_file_name):
    path = TRANSLATIONS_DIRECTORY / _ensure_json_extension(translation_file_name)
    if path.exists():
        raise ValueError(f'Tried to load non-existent translations file: {path}')

    global translations_config
    translations_config = Config(path)


def translate(key, *args, **kwargs):
    if key not in translations_config:
        raise ValueError(f'Translation not found: "{key}"')
    return translations_config[key].format(*args, **kwargs)
