from dataclasses import dataclass
from typing import Any, Callable, Optional

__all__ = [
    'AutoCastHandler',
    'AutoCastHandlerInfo',
    'get_auto_cast_handler_info',
    'has_auto_cast_default',
    'is_auto_cast_handler'
]


class AutoCastHandler:
    HANDLE_AUTO_CAST_FUNC_NAME = '_handle_auto_cast'
    HAS_AUTO_CAST_DEFAULT_FUNC_NAME = '_has_auto_cast_default'
    GET_AUTO_CAST_DEFAULT_FUNC_NAME = '_get_auto_cast_default'
    NO_DEFAULT_MARKER = object()

    @classmethod
    def _handle_auto_cast(cls, value: str):
        raise NotImplementedError(f'{cls} does not implement required class method {cls.HANDLE_AUTO_CAST_FUNC_NAME}')

    @classmethod
    def _has_auto_cast_default(cls) -> bool:
        return cls._get_auto_cast_default() is not cls.NO_DEFAULT_MARKER

    @classmethod
    def _get_auto_cast_default(cls) -> Any:
        return cls.NO_DEFAULT_MARKER


@dataclass
class AutoCastHandlerInfo:
    handler: Callable[[str], Any]
    default: Optional[Any] = None
    has_default: bool = False


def get_auto_cast_handler_info(obj: Any) -> Optional[AutoCastHandlerInfo]:
    handler = getattr(obj, AutoCastHandler.HANDLE_AUTO_CAST_FUNC_NAME, None)
    if handler is None:
        return None

    info = AutoCastHandlerInfo(handler)

    get_default = getattr(obj, AutoCastHandler.GET_AUTO_CAST_DEFAULT_FUNC_NAME)
    if get_default is not None and callable(get_default):
        default = get_default()
        if default is not AutoCastHandler.NO_DEFAULT_MARKER:
            info.default = default
            info.has_default = True

    return info


def has_auto_cast_default(obj: Any) -> bool:
    return getattr(obj, AutoCastHandler.HAS_AUTO_CAST_DEFAULT_FUNC_NAME, lambda: False)()

def is_auto_cast_handler(obj: Any) -> bool:
    return hasattr(obj, AutoCastHandler.HANDLE_AUTO_CAST_FUNC_NAME)