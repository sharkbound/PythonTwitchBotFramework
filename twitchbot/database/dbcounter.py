from sqlalchemy import Integer
from typing import Union, Optional, List

from .session import session
from .models import DBCounter

__all__ = ('counter_exist', 'get_all_counters', 'add_counter', 'increment_counter', 'increment_or_add_counter',
           'set_counter', 'delete_counter_by_id', 'delete_counter_by_alias',
           'get_counter_by_id', 'get_counter_by_alias', 'get_counter')


def counter_exist(channel: str, id: int = None, alias: str = None) -> bool:
    """return if counter exist that has the same ID or ALIAS or both"""

    if id is None and alias is None:
        return False

    filters = [DBCounter.channel == channel]

    if id is not None:
        filters.append(DBCounter.id == id)
    if alias is not None:
        filters.append(DBCounter.alias == alias)

    return bool(session.query(DBCounter).filter(*filters).count())


def add_counter(counter: DBCounter) -> bool:
    """adds a counter to the counter DB, return a bool indicating if it was successful"""
    assert isinstance(counter, DBCounter), 'counter must of type Counter'

    if counter_exist(counter.channel, counter.id, counter.alias):
        return False

    session.add(counter)
    session.commit()
    return True


def get_counter_by_id(channel: str, id: int) -> Optional[DBCounter]:
    assert isinstance(id, int), 'counter_id must be of type int'
    return session.query(DBCounter).filter(DBCounter.id == id, DBCounter.channel == channel).one_or_none()


def get_counter_by_alias(channel: str, alias: str) -> Optional[DBCounter]:
    assert isinstance(alias, str), 'counter_alias must be of type str'
    return session.query(DBCounter).filter(DBCounter.alias == alias, DBCounter.channel == channel).one_or_none()


def get_counter(channel: str, id_or_alias: Union[str, int]) -> Optional[DBCounter]:
    """
    tries to find counter by parsing x to int first (uses value if its already a int),
    then tries to find counter using x as a alias
    returns the counter if one exist, else None
    """
    try:
        return get_counter_by_id(channel, int(id_or_alias))
    except (ValueError, TypeError):
        return get_counter_by_alias(channel, str(id_or_alias))


def delete_counter_by_id(channel: str, id: int) -> None:
    assert isinstance(id, int), 'counter_id must be of type int'
    session.query(DBCounter).filter(DBCounter.channel == channel, DBCounter.id == id).delete()
    session.commit()


def delete_counter_by_alias(channel: str, alias: str) -> None:
    assert isinstance(alias, str), 'counter_alias must be of type str'
    session.query(DBCounter).filter(DBCounter.channel == channel, DBCounter.alias == alias).delete()
    session.commit()


def increment_counter(channel: str, id_or_alias: Union[str, int]) -> Optional[int]:
    """
    tries to set  the counter an returns the new counter value or None
    """
    cur_counter = get_counter(channel, id_or_alias)
    if cur_counter is None:
        return None

    cur_counter.value += 1

    session.commit()
    return cur_counter.value


def increment_or_add_counter(channel: str, alias: str) -> int:
    """
    if the counter does not exits it will be automatically created with the value 0
    the countervalue will be returned
    """

    if not counter_exist(channel=channel, alias=alias):
        counter = DBCounter.create(channel=channel, alias=alias)
        add_counter(counter)

    return increment_counter(channel, alias)


def set_counter(channel: str, id_or_alias: Union[str, int], new_value) -> Optional[int]:
    """
    tries to set counter an returns the new counter value or None
    """
    cur_counter = get_counter(channel, id_or_alias)
    if cur_counter is None:
        return None

    cur_counter.value = new_value

    session.commit()
    return cur_counter.value


def get_all_counters(channel: str) -> List[DBCounter]:
    """
    retrieve all counters from the current channel
    """
    return session.query(DBCounter).filter(DBCounter.channel == channel).all()

