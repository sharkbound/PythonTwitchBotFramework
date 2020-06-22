from asyncio import get_event_loop, gather
from itertools import chain
from typing import Any, Optional, TypeVar, Generator

from .enums import Event
from .events import trigger_event
from .modloader import trigger_mod_event
from .shared import get_bot

__all__ = [
    'forward_event'
]

_T = TypeVar('_T')


def forward_event(event: Event, *args: Any, channel: Optional[str] = None):
    """
    forwards a event to all event systems
    """
    loop = get_event_loop()
    loop.create_task(trigger_event(event, *args))
    loop.create_task(trigger_mod_event(event, *args, channel=channel))

    bot_event = getattr(get_bot(), event.name, None)
    if bot_event is not None and callable(bot_event):
        loop.create_task(bot_event(*args))


#                                                                                                Generator[YieldType, SendType, ReturnType]
async def forward_event_with_results(event: Event, *args: Any, channel: Optional[str] = None) -> Generator[Any, None, None]:
    """
    forwards a event to all event systems, then yield all the results though a generator
    :param event: event to forward
    :param args: the arguments that the event requires
    :param channel: the channel that causes the event
    """
    for result in await trigger_event(event, *args):
        yield result

    for result in await trigger_mod_event(event, *args, channel=channel):
        yield result

    bot_event = getattr(get_bot(), event.name, None)
    if bot_event is not None:
        yield await bot_event(*args)
