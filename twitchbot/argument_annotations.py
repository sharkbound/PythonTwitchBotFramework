from typing import Any

from .auto_cast_handler import AutoCastHandler

__all__ = [
    'OptionalIntArg',
    'OptionalStringArg',
    'BaseOptionalArg'
]


class BaseOptionalArg(AutoCastHandler):
    def __init__(self, value):
        self._value = value

    def get_or_default(self, default):
        if self.has_value:
            return self._value
        return default

    def get_or_none(self):
        return self._value

    @property
    def has_value(self):
        return self._value is not None

    @classmethod
    def _handle_auto_cast(cls, value: str):
        raise NotImplementedError

    @classmethod
    def _get_auto_cast_default(cls) -> Any:
        return cls(None)


class OptionalIntArg(BaseOptionalArg):
    def __init__(self, value):
        super().__init__(value)

    @classmethod
    def _handle_auto_cast(cls, value: str):
        try:
            return cls(int(value))
        except ValueError:
            return cls(None)


class OptionalStringArg(BaseOptionalArg):
    def __init__(self, value):
        super().__init__(value)

    @classmethod
    def _handle_auto_cast(cls, value: str):
        return cls(value)
