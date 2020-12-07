from pathlib import Path

_BOT_PACKAGE_PATH = Path()


def _set_bot_package_path(path: str):
    global _BOT_PACKAGE_PATH
    _BOT_PACKAGE_PATH = Path(path)
