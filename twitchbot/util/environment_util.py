import os

__all__ = (
    'is_env_key',
    'get_env_value'
)

from typing import Optional


def is_env_key(key) -> bool:
    return key.lower().startswith('env_')


def get_env_value(key, default=None) -> Optional[str]:
    if is_env_key(key):
        key = key[4:]

    value = os.environ.get(key, None)
    if value is None:
        return default
    return value
