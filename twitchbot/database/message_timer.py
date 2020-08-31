from asyncio import sleep, ensure_future
from typing import Optional, Dict, List

from .models import MessageTimer
from .session import session
from ..channel import channels

__all__ = ('get_message_timer', 'set_message_timer', 'message_timer_exist', 'set_message_timer_interval',
           'set_message_timer_message', 'delete_all_message_timers', 'delete_message_timer', 'set_message_timer_active',
           'active_message_timers', 'get_all_message_timers', 'restart_message_timer')

active_message_timers: Dict[str, MessageTimer] = {}


def timer_one_or_none(channel, *criteria) -> Optional[MessageTimer]:
    return session.query(MessageTimer).filter(MessageTimer.channel == channel, *criteria).one_or_none()


def get_message_timer(channel: str, name: str) -> Optional[MessageTimer]:
    """gets a MessageTimer instance from the database, return the MessageTimer if one is found, else None"""
    return timer_one_or_none(channel, MessageTimer.name == name)


def get_all_message_timers(channel: str) -> List[MessageTimer]:
    return session.query(MessageTimer).filter(MessageTimer.channel == channel).all()


def set_message_timer(channel: str, name: str, message: str, interval: float, active=False) -> None:
    """updates or adds a MessageTimer to the database"""
    timer = get_message_timer(channel, name)

    if timer:
        timer.message = message
        timer.interval = interval
    else:
        timer = MessageTimer.create(channel, name, message, interval)
        session.add(timer)

    session.commit()


def set_message_timer_interval(channel: str, name: str, interval: float) -> bool:
    """updates a MessageTimers interval, returns a bool if it was successful"""
    timer = get_message_timer(channel, name)

    if not timer:
        return False

    timer.interval = interval
    session.commit()
    return True


def set_message_timer_message(channel: str, name: str, message: str) -> bool:
    """updates a MessageTimers message, returns a bool if it was successful"""
    timer = get_message_timer(channel, name)

    if not timer:
        return False

    timer.message = message
    session.commit()
    return True


def set_message_timer_active(channel: str, name: str, value: bool) -> bool:
    """sets the timers active state in the database,
    if its already running it updates it as well,
    returns if it was successful"""

    key = _key(channel, name)
    timer = get_message_timer(channel, name)

    if not timer:
        return False

    if value:
        _start_message_timer(channel, name)
    else:
        _stop_message_timer(channel, name)

    timer.active = value
    session.commit()

    return True


def message_timer_exist(channel: str, name: str) -> bool:
    """checks if a timer exists, returns a bool"""
    return bool(session.query(MessageTimer).filter(MessageTimer.channel == channel, MessageTimer.name == name).count())


def delete_all_message_timers(channel: str):
    session.query(MessageTimer).filter(MessageTimer.channel == channel).delete()
    session.commit()


def delete_message_timer(channel: str, name: str) -> bool:
    """deletes a timers on the datebase, returns if it was successful"""
    timer = get_message_timer(channel, name)

    if not timer:
        return False

    if _key(channel, name) in active_message_timers:
        _stop_message_timer(channel, name)

    session.delete(timer)
    session.commit()
    return True


# fixme: bug with restarting a active message timer?
def restart_message_timer(channel: str, name: str):
    if _key(channel, name) in active_message_timers:
        set_message_timer_active(channel, name, False)

    set_message_timer_active(channel, name, True)


def _start_message_timer(channel: str, name: str) -> bool:
    """starts a message timer, returns if it was successful"""
    key = _key(channel, name)
    timer = active_message_timers.get(key)

    if not timer:
        timer = get_message_timer(channel, name)

    if timer is None or timer.running:
        return False

    channel = channels.get(channel)

    if not channel:
        return False

    if not timer.running:
        timer.task = ensure_future(_message_timer_say_loop(channel, timer))

    active_message_timers[key] = timer
    return True


def _stop_message_timer(channel: str, name: str) -> bool:
    """stops a message timer, returns if it was successful"""
    key = _key(channel, name)
    timer = active_message_timers.get(key)

    if not timer:
        return False

    if not timer.running or timer.task is None:
        return False

    timer.task.cancel()
    del active_message_timers[key]

    return True


async def _message_timer_say_loop(channel, timer):
    while True:
        await sleep(timer.interval)
        await channel.send_message(timer.message)


def _key(channel, name):
    return f'{channel}_{name}'
