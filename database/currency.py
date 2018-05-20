from typing import Dict, Tuple

from .models import Balance, CurrencyName
from .session import session

currency_name_cache: Dict[Tuple[str, str], CurrencyName] = {}


def set_balance(channel: str, user: str, value: int) -> None:
    get_balance(channel, user).balance = value
    session.commit()


def add_balance(channel: str, user: str, value: int) -> None:
    get_balance(channel, user).balance += value
    session.commit()


def get_balance(channel: str, user: str) -> Balance:
    """gets the balance of the user for the specified channel"""
    bal = session.query(Balance).filter(Balance.channel == channel, Balance.user == user).one_or_none()

    if bal is None:
        bal = Balance.create(channel, user)
        session.add(bal)
        session.commit()

    return bal


def get_balance_from_msg(msg) -> Balance:
    """gets the balance for the user from the channel the msg came from"""
    return get_balance(msg.channel_name, msg.author)


def get_currency_name(channel: str) -> CurrencyName:
    """returns a CurrencyName object for the channel specifed, returns None if it doesnt exist"""
    if channel in currency_name_cache:
        return currency_name_cache[channel]

    currency = session.query(CurrencyName).filter(CurrencyName.channel == channel).one_or_none()
    if currency is None:
        currency = CurrencyName.create(channel, 'points')
        session.add(currency)
        session.commit()

    currency_name_cache[channel] = currency
    return currency


def set_currency_name(channel: str, new_name: str) -> bool:
    """sets a channels currency name, return if it was successful"""
    if not new_name:
        return False

    currency = get_currency_name(channel)

    if currency is None:
        session.add(CurrencyName.create(channel, new_name))
    else:
        currency.name = new_name

    currency_name_cache[channel] = currency
    session.commit()
    return True
