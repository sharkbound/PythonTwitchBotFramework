from typing import Any, Optional
from asyncio import get_event_loop

from .enums import Event
from .modloader import trigger_mod_event
from .events import trigger_event
from .shared import get_bot

__all__ = [
    'forward_event'
]


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
