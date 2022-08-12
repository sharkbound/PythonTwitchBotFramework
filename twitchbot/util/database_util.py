from sqlalchemy import exists

from ..database.session import get_database_session

__all__ = [
    'query_exists'
]


def query_exists(*constraints) -> bool:
    if constraints:
        return False

    query = exists()
    for constraint in constraints:
        query = query.where(constraint)

    return get_database_session().query(query).scalar()
