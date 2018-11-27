from collections import namedtuple
from datetime import datetime, timedelta
from secrets import choice
from typing import Dict, Optional, Tuple

__all__ = (
    'accept_duel',
    'duel_exists',
    'DUEL_DURATION',
    'add_duel',
    'remove_duel',
    'duel_expired',
    'Duel',
    'get_duel'
)


def _key(channel: str, challenger: str, target: str):
    return channel, challenger, target


Duel = namedtuple('Duel', 'challenger target bet time')
DUEL_DURATION = timedelta(seconds=30)

# keys are: (channel, challenger, target)
# keeps track of all pending duels
pending_duels: Dict[Tuple[str, str, str], Duel] = {}


def duel_expired(duel: Duel) -> bool:
    return datetime.now() - duel.time > DUEL_DURATION


def duel_exists(channel: str, challenger: str, target: str) -> bool:
    """
    returns True if a duel exist, else False

    :param channel: the channel which the challenger / target is in
    :param challenger: the user who initiated the duel
    :param target: the user who is being challenged
    :return: True if a duel exist between challenger and target, else False
    """
    return _key(channel, challenger, target) in pending_duels


def add_duel(channel: str, challenger: str, target: str, bet: int):
    """
    adds a new pending duel

    :param channel: the channel which the challenger / target is in
    :param challenger: the user who initiated the duel
    :param target: the user who is being challenged
    :param bet: the bet that the winner takes, and the loser loses
    """
    key = _key(channel, challenger, target)
    pending_duels[key] = Duel(challenger, target, bet, datetime.now())


def remove_duel(channel: str, challenger: str, target: str):
    key = _key(channel, challenger, target)
    if key in pending_duels:
        del pending_duels[key]


def get_duel(channel: str, challenger: str, target: str) -> Optional[Duel]:
    """
    gets a pending duel, if duel does not exist, return None

    :param channel: the channel which the challenger / target is in
    :param challenger: the user who initialized the duel
    :param target: the user who was challenged
    :return: duel if it exists, else None
    """
    return pending_duels.get(_key(channel, challenger, target))


def accept_duel(channel: str, challenger: str, target: str) -> Tuple[Optional[str], Optional[int]]:
    """
    accepts a duel from [target] issued by [challenger]
    returns tuple of (winner, bet) if duel exists and has not expired, else (None, None)

    :param channel: the channel which the challenger / target is in
    :param challenger: the user who initialized a challenge to [target]
    :param target: the user who was challenged
    :return: (winner, bet) if duel exists and has not expired, else (None, None)
    """
    duel = get_duel(channel, challenger, target)
    remove_duel(channel, challenger, target)

    if not duel or duel_expired(duel):
        return None, None

    return choice((challenger, target)), duel.bet
