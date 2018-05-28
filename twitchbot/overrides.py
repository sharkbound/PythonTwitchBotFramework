from .enums import Event

overrides = {}


def override_event(event: Event):
    def _func(func):
        overrides[event] = func

    return _func
