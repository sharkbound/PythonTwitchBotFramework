import sqlalchemy.orm
from sqlalchemy import exists

__all__ = [
    'query_exists'
]


def query_exists(session: sqlalchemy.orm.scoped_session, *constraints) -> bool:
    if not constraints:
        return False

    query = exists()
    for constraint in constraints:
        query = query.where(constraint)

    return session.query(query).scalar()
