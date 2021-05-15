from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
import os

from ..config import database_cfg

__all__ = ('Base', 'engine', 'get_database_session', 'DB_FILENAME', 'init_tables', 'session')


def _try_get_env(value: str):
    if value.lower().startswith('env_'):
        if value[4:] not in os.environ:
            print('----------DATABASE ERROR----------')
            print(f'missing environment variable/key: {value[4:]}')
            input('\npress enter to exit...')
            exit(1)
        return os.environ[value[4:]]
    return value


Base = declarative_base()
DB_FILENAME = 'database.sqlite'
try:
    engine = create_engine(f'sqlite:///{DB_FILENAME}'
                           if not database_cfg.enabled else
                           database_cfg.connection.format(
                               database_format=_try_get_env(database_cfg.database_format),
                               driver=_try_get_env(database_cfg.driver),
                               username=_try_get_env(database_cfg.username),
                               password=_try_get_env(database_cfg.password),
                               address=_try_get_env(database_cfg.address),
                               port=_try_get_env(database_cfg.port),
                               database=_try_get_env(database_cfg.database)
                           ),
                           pool_recycle=3600)
except (ImportError, ModuleNotFoundError):
    print(
        f'Could not find library for database driver "{database_cfg.driver}", please install the necessary driver.\n'
        f'for mysql, install this driver (via pip): pip install --upgrade mysql-connector-python')
    input('\npress enter to exit...')
    exit(1)

# noinspection PyUnboundLocalVariable
Session = orm.sessionmaker(bind=engine)
# get_database_session() should be favored here
session = orm.scoped_session(Session)


def get_database_session():
    # mainly here for future usage, mainly for issues regarding connection maintaining.
    # as of now i am trying out pool_recycle=3600 (60 minutes) to see if it solves the issue
    global session
    return session


def init_tables():
    Base.metadata.create_all(engine)
