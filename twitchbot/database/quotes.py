from typing import Union, Optional
from .models import Quote
from .session import session

__all__ = ('quote_exist', 'add_quote', 'get_quote', 'get_quote_by_alias', 'get_quote_by_id', 'delete_all_quotes',
           'delete_quote_by_alias', 'delete_quote_by_id')


def quote_exist(channel: str, id: int = None, alias: str = None) -> bool:
    """return if quote exist that has the same ID or ALIAS or both"""

    if id is None and alias is None:
        return False

    filters = [Quote.channel == channel]

    if id is not None:
        filters.append(Quote.id == id)
    if alias is not None:
        filters.append(Quote.alias == alias)

    return bool(session.query(Quote).filter(*filters).count())


def add_quote(quote: Quote) -> bool:
    """adds a quote to the quote DB, return a bool indicating if it was successful"""
    assert isinstance(quote, Quote), 'quote must of type Quote'

    if quote_exist(quote.channel, quote.id, quote.alias):
        return False

    session.add(quote)
    session.commit()
    return True


def get_quote_by_id(channel: str, id: int) -> Optional[Quote]:
    assert isinstance(id, int), 'quote_id must be of type int'
    return session.query(Quote).filter(Quote.id == id, Quote.channel == channel).one_or_none()


def get_quote_by_alias(channel: str, alias: str) -> Optional[Quote]:
    assert isinstance(alias, str), 'quote_alias must be of type str'
    return session.query(Quote).filter(Quote.alias == alias, Quote.channel == channel).one_or_none()


def get_quote(channel: str, id_or_alias: Union[str, int]) -> Optional[Quote]:
    """
    tries to find quote by parsing x to int first (uses value if its already a int),
    then tries to find quote using x as a alias
    returns the quote if one exist, else None
    """
    try:
        return get_quote_by_id(channel, int(id_or_alias))
    except ValueError:
        return get_quote_by_alias(channel, str(id_or_alias))


def delete_quote_by_id(channel: str, id: int) -> None:
    assert isinstance(id, int), 'quote_id must be of type int'
    session.query(Quote).filter(Quote.channel == channel, Quote.id == id).delete()
    session.commit()


def delete_quote_by_alias(channel: str, alias: str) -> None:
    assert isinstance(alias, str), 'quote_alias must be of type str'
    session.query(Quote).filter(Quote.channel == channel, Quote.alias == alias).delete()
    session.commit()


def delete_all_quotes():
    session.query(Quote).delete()
    session.commit()
