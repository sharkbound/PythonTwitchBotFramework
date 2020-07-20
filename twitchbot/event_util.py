from asyncio import get_event_loop, gather
from itertools import chain
from typing import Any, Optional, TypeVar, Union, Callable, Coroutine, TYPE_CHECKING

from .enums import Event
from .events import trigger_event
from .modloader import trigger_mod_event
from .shared import get_bot

if TYPE_CHECKING:
    from .channel import Channel
    from .message import Message

__all__ = [
    'forward_event',
    'forward_event_with_results'
]

_T = TypeVar('_T')


def _get_channel_name(value: Union['Channel', 'Message', str]):
    from .channel import Channel
    from .message import Message

    if isinstance(value, Channel):
        return value.name

    if isinstance(value, str):
        return value

    if isinstance(value, Message):
        return value.channel_name

    raise ValueError(f'[EVENT CHANNEL ERROR] got type {type(value)}, expected: {Channel}, {Message}, or {str}')


def _get_bot_event(event: Event, default: Callable = None) -> Callable:
    """
    tries to get the bots event handler for the event passed in,
    returns default if it is not None on failure, or a NOP (no operation) placeholder function

    :param event:
    :param default:
    :return:
    """

    async def _nop(*_):
        return None

    func = getattr(get_bot(), event.name, None)
    return (
        func
        if func is not None and callable(func)
        else (default or _nop)
    )


async def _wrap_async_result_with_list(coro: Coroutine):
    return [await coro]


def forward_event(event: Event, *args: Any, channel: Union['Channel', 'Message', str] = ''):
    """
    forwards a event to all event systems
    """
    channel = _get_channel_name(channel)

    loop = get_event_loop()
    loop.create_task(trigger_event(event, *args))
    loop.create_task(trigger_mod_event(event, *args, channel=channel))
    loop.create_task(_get_bot_event(event)(*args))


async def forward_event_with_results(
        event: Event,
        *args: Any,
        channel: Union['Channel', 'Message', str] = '',
        allow_none_results: bool = False) -> list:
    """
    forwards a event to all event systems, then yield all the results though a generator
    :param event: event to forward
    :param args: the arguments that the event requires
    :param channel: the channel that causes the event
    :param allow_none_results: if True, results may can include None returns, else None's are filtered out
    """

    channel = _get_channel_name(channel)
    # predicate (condition) that results are valid and returned
    # awaitable future that collects all the event results
    result_fetcher = gather(
        trigger_event(event, *args),
        trigger_mod_event(event, *args, channel=channel),
        _wrap_async_result_with_list(_get_bot_event(event)(*args)),
    )

    return [
        value
        for value in chain.from_iterable(await result_fetcher)
        if allow_none_results or value is not None
    ]
