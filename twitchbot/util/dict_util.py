import json
from typing import Any

__all__ = [
    'dict_get_value',
    'dict_has_keys',
    'try_parse_json',
]


def dict_has_keys(data: dict, *keys) -> bool:
    for key in keys:
        if not isinstance(data, dict):
            return False

        if key not in data:
            return False

        data = data[key]

    return True


def dict_get_value(data: dict, *keys, default: Any = None) -> Any:
    for key in keys:
        try:
            data = data[key]
        except (TypeError, IndexError, KeyError):
            return default

    return data


def try_parse_json(data: str, **default_keys) -> dict:
    try:
        return json.loads(data)
    except (TypeError, json.JSONDecodeError) as _:
        return default_keys
