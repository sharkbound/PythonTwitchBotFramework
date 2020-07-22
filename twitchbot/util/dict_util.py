from typing import Any

__all__ = [
    'dict_get_path',
    'dict_has_keys',
]


def dict_has_keys(data: dict, *keys) -> bool:
    for key in keys:
        if not isinstance(data, dict):
            return False

        if key not in data:
            return False

        data = data[key]

    return True


def dict_get_path(data: dict, *keys, default: Any = None) -> Any:
    for key in keys:
        try:
            data = data[key]
        except (TypeError, IndexError, KeyError):
            return default

    return data
