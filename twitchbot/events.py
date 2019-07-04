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
    def _func(func):
        custom_event_handlers[event].append(func)
        return func

    return _func
