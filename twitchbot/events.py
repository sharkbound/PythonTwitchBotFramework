import traceback
from collections import defaultdict
from typing import DefaultDict, Callable, List

from .enums import Event

custom_event_handlers: DefaultDict[Event, List[Callable]] = defaultdict(list)


async def trigger_event(event: Event, *args) -> list:
    out = []
    for handler in custom_event_handlers[event]:
        try:
            out.append(await handler(*args))
        except Exception as e:
            print(f'\nerror has occurred while triggering a custom event on a mod, details:\n'
                  f'event: {event}\n'
                  f'error: {type(e)}\n'
                  f'reason: {e}\n'
                  f'stack trace:')
            traceback.print_exc()
    return out


def event_handler(event: Event):
    def _register(func):
        custom_event_handlers[event].append(func)
        return AsyncEventWrapper(func, type=event)

    return _register


class AsyncEventWrapper:
    def __init__(self, func, type: Event):
        self.func = func
        self.type = type

    def unregister(self):
        events = custom_event_handlers[self.type]
        if self.func in events:
            events.remove(self.func)

    async def __call__(self, *args, **kwargs):
        await self.func(args, **kwargs)
