from pathlib import Path

_bot_package_path = Path()


def _set_bot_package_path(path: str):
    global _bot_package_path
    _bot_package_path = Path(path)


def get_bot_package_path():
    return _bot_package_path
